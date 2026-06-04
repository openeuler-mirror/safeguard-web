"""自动装机视图集"""
import subprocess
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.models.host import Host
from backend.models.osdeploy import KickStartFileStatus, RepoStatus, WhiteList
from backend.models.task import Task
from backend.services.osdeploy.deploy_service import DeployService
from backend.services.osdeploy.pxe_service import PXEService
from backend.services.osdeploy.dhcp_service import DHCPService
from backend.services.task import TaskService
from backend.common import SuccessResponse, ErrorResponse, ErrCode
from backend.utils.ssh import SSHClient
from backend.schemas.osdeploy import AutoInstallRequestSchema


class AutoInstallViewSet(viewsets.ViewSet):
    """自动装机视图集"""
    permission_classes = [IsAuthenticated]

    @action(['post'], False)
    def auto_install(self, request):
        """自动装机入口"""
        schema = AutoInstallRequestSchema(**request.data)
        job = DeployService.start_auto_install(
            host_id=schema.host_id,
            kickstart_id=schema.kickstart_id,
            repo_id=schema.repo_id,
        )
        # Celery 异步执行装机（替代 threading.Thread）
        from backend.tasks.osdeploy import auto_install_os
        auto_install_os.delay(job.job_id, schema.host_id, schema.kickstart_id, schema.repo_id)
        return SuccessResponse({"job_id": job.job_id, "status": "started"})

    @action(['post'], False)
    def single_install(self, request):
        """单台装机"""
        return self.auto_install(request)

    @action(['post'], False)
    def batch_install(self, request):
        """批量装机"""
        hosts = request.data.get("hosts", [])
        kickstart_id = request.data.get("kickstart_id")
        repo_id = request.data.get("repo_id")
        job_ids = []
        for host_id in hosts:
            job = DeployService.start_auto_install(
                host_id=host_id,
                kickstart_id=kickstart_id,
                repo_id=repo_id,
            )
            job_ids.append(job.job_id)
            from backend.tasks.osdeploy import auto_install_os
            auto_install_os.delay(job.job_id, host_id, kickstart_id, repo_id)
        return SuccessResponse({"job_ids": job_ids, "status": "started"})

    def _do_auto_install(self, job_id: str, host_id: int, kickstart_id: int, repo_id: int):
        """执行自动装机流程"""
        try:
            TaskService.update_job(job_id, status="running", progress=10)
            # 1. 获取主机信息
            host = Host.objects.get(pk=host_id)
            # 2. 获取Kickstart和仓库
            kickstart = KickStartFileStatus.objects.get(pk=kickstart_id)
            repo = RepoStatus.objects.get(pk=repo_id)
            # 3. 生成PXE启动配置
            pxe_server = DHCPService.get_pxe_server()
            if not pxe_server:
                raise ValueError("未配置PXE服务器")
            ks_url = PXEService.get_ks_url(pxe_server.server_ip, kickstart.name)
            repo_url = PXEService.get_repo_url(pxe_server.server_ip, repo.name)
            mac_address = host.mac_address or "00:00:00:00:00:00"
            # 4. 写入PXE启动文件
            pxe_content = PXEService.generate_pxe_boot_file(mac_address, ks_url, repo_url)
            PXEService.write_pxe_boot_file(mac_address, pxe_content)
            TaskService.update_job(job_id, progress=30)
            # 5. 添加DHCP静态条目
            DHCPService.add_static_entry(mac_address, host.ip_address or "", host.hostname)
            TaskService.update_job(job_id, progress=50)
            # 6. 重启目标主机（优先SSH，其次IPMI）
            self._reboot_host(host)
            TaskService.update_job(job_id, progress=70)
            # 7. 轮询安装状态
            install_success = self._poll_install_status(host, timeout=3600)
            if install_success:
                TaskService.update_job(job_id, status="success", progress=100,
                    result={"message": "装机任务已完成"})
            else:
                raise TimeoutError("装机状态轮询超时")
        except Exception as e:
            TaskService.update_job(job_id, status="failed", progress=0,
                error_message=str(e))
        finally:
            # 清理PXE配置和DHCP白名单
            try:
                host = Host.objects.get(pk=host_id)
                PXEService.remove_pxe_boot_file(host.mac_address or "00:00:00:00:00:00")
                DHCPService.remove_static_entry(host.mac_address or "00:00:00:00:00:00")
            except Exception:
                pass

    def _reboot_host(self, host: Host):
        """重启目标主机，优先SSH，其次IPMI"""
        # 尝试SSH重启
        if host.ip_address and host.username and host.password:
            try:
                ssh = SSHClient(
                    host=str(host.ip_address),
                    port=host.port or 22,
                    username=host.username,
                    password=host.password,
                    timeout=10,
                )
                stdout, stderr, exit_code = ssh.execute_command("reboot")
                ssh.close()
                if exit_code in (0, -1):  # reboot 通常会断开连接
                    return
            except Exception:
                pass
        # 尝试IPMI重启
        if host.ipmi_address and host.ipmi_user and host.ipmi_password:
            import subprocess
            try:
                subprocess.run(
                    [
                        "ipmitool", "-I", "lanplus",
                        "-H", str(host.ipmi_address),
                        "-U", host.ipmi_user,
                        "-P", host.ipmi_password,
                        "chassis", "power", "reset",
                    ],
                    capture_output=True, timeout=15,
                )
                return
            except Exception:
                pass
        raise RuntimeError("无法重启目标主机：SSH和IPMI均不可用")

    def _poll_install_status(self, host: Host, timeout: int = 3600, interval: int = 30) -> bool:
        """轮询安装状态，通过SSH连接判断主机是否恢复"""
        import time
        elapsed = 0
        while elapsed < timeout:
            time.sleep(interval)
            elapsed += interval
            try:
                ssh = SSHClient(
                    host=str(host.ip_address),
                    port=host.port or 22,
                    username=host.username,
                    password=host.password,
                    timeout=10,
                )
                stdout, stderr, exit_code = ssh.execute_command("echo 'install-check'")
                ssh.close()
                if exit_code == 0 and "install-check" in stdout:
                    return True
            except Exception:
                pass
        return False
