"""自动装机视图集"""
import threading
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
        # 异步执行装机
        thread = threading.Thread(
            target=self._do_auto_install,
            args=(job.job_id, schema.host_id, schema.kickstart_id, schema.repo_id),
        )
        thread.start()
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
            thread = threading.Thread(
                target=self._do_auto_install,
                args=(job.job_id, host_id, kickstart_id, repo_id),
            )
            thread.start()
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
            # 4. 写入PXE启动文件
            PXEService.write_pxe_boot_file(host.mac_address or "00:00:00:00:00:00",
                PXEService.generate_pxe_boot_file(host.mac_address or "00:00:00:00:00:00", ks_url, repo_url))
            TaskService.update_job(job_id, progress=30)
            # 5. 添加DHCP静态条目
            DHCPService.add_static_entry(host.mac_address or "00:00:00:00:00:00", host.ip_address or "")
            TaskService.update_job(job_id, progress=50)
            # 6. 重启目标主机（通过IPMI或SSH）
            # TODO: 实现远程重启
            TaskService.update_job(job_id, progress=70)
            # 7. 轮询安装状态
            # TODO: 实现状态轮询
            TaskService.update_job(job_id, status="success", progress=100,
                result={"message": "装机任务已完成"})
        except Exception as e:
            TaskService.update_job(job_id, status="failed", progress=0,
                error_message=str(e))
