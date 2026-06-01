"""Safeguard 部署服务"""
import logging
import subprocess
import threading
import os
from typing import Optional, List
from backend.models.security import SafeguardDeploy
from backend.services.task import TaskService
from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)


class SafeguardService:
    """Safeguard 部署服务"""

    @staticmethod
    def list_safeguards(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取部署记录列表（支持分页和过滤）"""
        queryset = SafeguardDeploy.objects.all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_safeguard(safeguard_id: int) -> Optional[SafeguardDeploy]:
        """获取部署记录详情"""
        try:
            return SafeguardDeploy.objects.get(pk=safeguard_id)
        except SafeguardDeploy.DoesNotExist:
            return None

    @staticmethod
    def create_safeguard(data: dict) -> SafeguardDeploy:
        """创建部署记录"""
        safeguard = SafeguardDeploy.objects.create(
            name=data.get('name'),
            target_hosts=data.get('target_hosts', []),
            safeguard_type=data.get('safeguard_type', 'safeguardx86'),
            arch=data.get('arch', 'x86'),
            host=data.get('host', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            port=data.get('port', '22'),
            description=data.get('description', ''),
        )
        return safeguard

    @staticmethod
    def update_safeguard(safeguard_id: int, data: dict) -> Optional[SafeguardDeploy]:
        """更新部署记录"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
            if 'name' in data:
                safeguard.name = data['name']
            if 'target_hosts' in data:
                safeguard.target_hosts = data['target_hosts']
            if 'safeguard_type' in data:
                safeguard.safeguard_type = data['safeguard_type']
            if 'arch' in data:
                safeguard.arch = data['arch']
            if 'host' in data:
                safeguard.host = data['host']
            if 'username' in data:
                safeguard.username = data['username']
            if 'password' in data:
                safeguard.password = data['password']
            if 'port' in data:
                safeguard.port = data['port']
            if 'status' in data:
                safeguard.status = data['status']
            if 'description' in data:
                safeguard.description = data['description']
            safeguard.save()
            return safeguard
        except SafeguardDeploy.DoesNotExist:
            return None

    @staticmethod
    def delete_safeguard(safeguard_id: int) -> bool:
        """删除部署记录"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
            safeguard.delete()
            return True
        except SafeguardDeploy.DoesNotExist:
            return False

    @staticmethod
    def deploy(safeguard_id: int) -> bool:
        """执行部署（异步），创建 Task 追踪"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
        except SafeguardDeploy.DoesNotExist:
            return False

        # 创建 Task 记录用于追踪
        task = TaskService.create_job(
            job_type='safeguard_deploy',
            target=f'safeguard_{safeguard_id}',
            status='running',
            progress=0,
        )
        safeguard.status = 'running'
        safeguard.result = {'task_id': task.job_id}
        safeguard.save()

        # 异步执行部署
        thread = threading.Thread(
            target=SafeguardService._deploy_async,
            args=(safeguard_id, task.job_id),
        )
        thread.start()
        return True

    @staticmethod
    def _deploy_async(safeguard_id: int, task_job_id: str):
        """异步执行部署"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)

            # 根据是否远程执行不同的部署逻辑
            if not safeguard.host:
                SafeguardService._deploy_local(safeguard, task_job_id)
            else:
                SafeguardService._deploy_remote(safeguard, task_job_id)

            TaskService.update_job(task_job_id, status='success', progress=100,
                result={'message': '部署成功'})
            safeguard.status = 'success'
            safeguard.result = {'message': '部署成功', 'task_id': task_job_id}
        except Exception as e:
            logger.error(f"部署失败 safeguard_id={safeguard_id}: {e}")
            TaskService.update_job(task_job_id, status='failed', progress=0,
                error_message=str(e))
            safeguard.status = 'failed'
            safeguard.error_message = str(e)
            safeguard.result = {'error': str(e), 'task_id': task_job_id}
        finally:
            safeguard.save()

    @staticmethod
    def _deploy_local(safeguard: SafeguardDeploy, task_job_id: str):
        """本地部署"""
        TaskService.update_job(task_job_id, progress=10, result={'step': '准备本地部署环境'})
        install_dir = '/opt/safeguard'
        os.makedirs(install_dir, exist_ok=True)

        TaskService.update_job(task_job_id, progress=30, result={'step': '安装 Safeguard 包'})
        # 根据架构选择安装方式
        if safeguard.arch == 'arm':
            pkg_name = 'safeguard-arm64.rpm'
        else:
            pkg_name = 'safeguard-x86_64.rpm'

        # 尝试 yum/dnf 安装
        result = subprocess.run(
            ['yum', 'install', '-y', pkg_name],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            # 尝试 rpm 直接安装
            result = subprocess.run(
                ['rpm', '-ivh', pkg_name],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"本地安装失败: {result.stderr}")

        TaskService.update_job(task_job_id, progress=60, result={'step': '配置 Safeguard'})
        # 写入配置文件
        config_path = os.path.join(install_dir, 'config.toml')
        with open(config_path, 'w') as f:
            f.write(f"[safeguard]\ntype = '{safeguard.safeguard_type}'\narch = '{safeguard.arch}'\n")

        TaskService.update_job(task_job_id, progress=80, result={'step': '启动 Safeguard 服务'})
        result = subprocess.run(
            ['systemctl', 'start', 'safeguard'],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            logger.warning(f"启动 safeguard 服务失败: {result.stderr}")

        TaskService.update_job(task_job_id, progress=95, result={'step': '验证部署结果'})
        result = subprocess.run(
            ['systemctl', 'is-active', 'safeguard'],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("Safeguard 服务未能正常运行")

    @staticmethod
    def _deploy_remote(safeguard: SafeguardDeploy, task_job_id: str):
        """远程SSH部署"""
        TaskService.update_job(task_job_id, progress=10, result={'step': '连接远程主机'})
        ssh = SSHClient(
            host=safeguard.host,
            port=int(safeguard.port) if safeguard.port else 22,
            username=safeguard.username,
            password=safeguard.password,
            timeout=30,
        )
        if not ssh.connect():
            raise ConnectionError(f"无法连接到远程主机 {safeguard.host}")

        try:
            TaskService.update_job(task_job_id, progress=25, result={'step': '创建远程安装目录'})
            remote_dir = '/opt/safeguard'
            ssh.create_dir_recursive(remote_dir)

            TaskService.update_job(task_job_id, progress=40, result={'step': '上传安装包并安装'})
            pkg_name = 'safeguard-arm64.rpm' if safeguard.arch == 'arm' else 'safeguard-x86_64.rpm'
            remote_pkg = f"{remote_dir}/{pkg_name}"
            # 注意：这里假设本地有安装包，实际应使用 upload_file
            # 暂用 wget 下载作为示例
            stdout, stderr, exit_code = ssh.execute_command(
                f"wget -q -O {remote_pkg} http://repo.local/{pkg_name} || true"
            )

            # 尝试安装
            stdout, stderr, exit_code = ssh.execute_command(
                f"yum install -y {remote_pkg} || rpm -ivh {remote_pkg}"
            )
            if exit_code != 0:
                raise RuntimeError(f"远程安装失败: {stderr}")

            TaskService.update_job(task_job_id, progress=65, result={'step': '配置 Safeguard'})
            config_content = f"[safeguard]\ntype = '{safeguard.safeguard_type}'\narch = '{safeguard.arch}'\n"
            stdout, stderr, exit_code = ssh.execute_command(
                f"cat > {remote_dir}/config.toml << 'EOF'\n{config_content}\nEOF"
            )

            TaskService.update_job(task_job_id, progress=80, result={'step': '启动服务'})
            stdout, stderr, exit_code = ssh.execute_command("systemctl start safeguard || true")

            TaskService.update_job(task_job_id, progress=95, result={'step': '验证服务状态'})
            stdout, stderr, exit_code = ssh.execute_command("systemctl is-active safeguard")
            if exit_code != 0:
                raise RuntimeError("远程 Safeguard 服务未能正常运行")
        finally:
            ssh.close()

    @staticmethod
    def rollback(safeguard_id: int) -> bool:
        """回滚部署"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
        except SafeguardDeploy.DoesNotExist:
            return False

        task = TaskService.create_job(
            job_type='safeguard_rollback',
            target=f'safeguard_{safeguard_id}',
            status='running',
            progress=0,
        )
        safeguard.status = 'running'
        safeguard.result = {'task_id': task.job_id, 'action': 'rollback'}
        safeguard.save()

        thread = threading.Thread(
            target=SafeguardService._rollback_async,
            args=(safeguard_id, task.job_id),
        )
        thread.start()
        return True

    @staticmethod
    def _rollback_async(safeguard_id: int, task_job_id: str):
        """异步执行回滚"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
            TaskService.update_job(task_job_id, progress=20, result={'step': '停止 Safeguard 服务'})

            if safeguard.host:
                ssh = SSHClient(
                    host=safeguard.host,
                    port=int(safeguard.port) if safeguard.port else 22,
                    username=safeguard.username,
                    password=safeguard.password,
                    timeout=30,
                )
                if ssh.connect():
                    try:
                        ssh.execute_command("systemctl stop safeguard || true")
                        TaskService.update_job(task_job_id, progress=50, result={'step': '卸载 Safeguard'})
                        ssh.execute_command("rpm -e safeguard || true")
                        ssh.execute_command("rm -rf /opt/safeguard")
                    finally:
                        ssh.close()
            else:
                subprocess.run(['systemctl', 'stop', 'safeguard'], capture_output=True)
                TaskService.update_job(task_job_id, progress=50, result={'step': '卸载 Safeguard'})
                subprocess.run(['rpm', '-e', 'safeguard'], capture_output=True)
                subprocess.run(['rm', '-rf', '/opt/safeguard'], capture_output=True)

            TaskService.update_job(task_job_id, status='success', progress=100,
                result={'message': '回滚成功'})
            safeguard.status = 'pending'
            safeguard.error_message = ''
            safeguard.result = {'message': '回滚成功'}
        except Exception as e:
            logger.error(f"回滚失败 safeguard_id={safeguard_id}: {e}")
            TaskService.update_job(task_job_id, status='failed', progress=0,
                error_message=str(e))
            safeguard.status = 'failed'
            safeguard.error_message = str(e)
        finally:
            safeguard.save()

    @staticmethod
    def get_deploy_status(safeguard_id: int) -> Optional[dict]:
        """获取部署状态（包含 Task 进度）"""
        try:
            safeguard = SafeguardDeploy.objects.get(pk=safeguard_id)
            result = {
                'status': safeguard.status,
                'result': safeguard.result,
                'error_message': safeguard.error_message,
            }
            # 如果有 Task 记录，合并 Task 进度
            task_id = safeguard.result.get('task_id') if safeguard.result else None
            if task_id:
                task = TaskService.get_job(task_id)
                if task:
                    result['task'] = {
                        'job_id': task.job_id,
                        'status': task.status,
                        'progress': task.progress,
                        'error_message': task.error_message,
                    }
            return result
        except SafeguardDeploy.DoesNotExist:
            return None