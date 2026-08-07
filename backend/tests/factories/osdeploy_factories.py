"""OS部署相关测试数据工厂"""
import uuid
from backend.models.osdeploy import (
    JobStatus,
    RepoStatus,
    PXEServerStatus,
    KickStartFileStatus,
    ISOFileStatus,
    WhiteList,
    OutIpSN,
    SensorData,
)


class JobStatusFactory:
    """任务状态工厂"""

    @staticmethod
    def create(job_id=None, job_type="os_install", target=None, status="pending", progress=0, **kwargs):
        """创建任务状态"""
        return JobStatus.objects.create(
            job_id=job_id or f"job-{uuid.uuid4().hex[:8]}",
            job_type=job_type,
            target=target or "192.168.1.100",
            status=status,
            progress=progress,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建任务状态"""
        jobs = []
        for i in range(count):
            jobs.append(JobStatusFactory.create(**kwargs))
        return jobs

    @staticmethod
    def create_running(**kwargs):
        """创建运行中的任务"""
        return JobStatusFactory.create(status="running", progress=50, **kwargs)

    @staticmethod
    def create_success(**kwargs):
        """创建成功的任务"""
        return JobStatusFactory.create(status="success", progress=100, **kwargs)

    @staticmethod
    def create_failed(error_message="Test error", **kwargs):
        """创建失败的任务"""
        return JobStatusFactory.create(status="failed", progress=30, error_message=error_message, **kwargs)


class RepoStatusFactory:
    """仓库状态工厂"""

    @staticmethod
    def create(name=None, repo_type="yum", base_url=None, is_default=False, status="active", **kwargs):
        """创建仓库状态"""
        return RepoStatus.objects.create(
            name=name or f"repo-{uuid.uuid4().hex[:6]}",
            repo_type=repo_type,
            base_url=base_url or "http://repo.example.com/yum",
            is_default=is_default,
            status=status,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建仓库"""
        repos = []
        for i in range(count):
            repos.append(RepoStatusFactory.create(**kwargs))
        return repos

    @staticmethod
    def create_default(**kwargs):
        """创建默认仓库"""
        return RepoStatusFactory.create(is_default=True, **kwargs)


class WhiteListFactory:
    """MAC地址白名单工厂"""

    @staticmethod
    def create(mac_address=None, hostname=None, ip_address=None, is_active=True, **kwargs):
        """创建白名单"""
        return WhiteList.objects.create(
            mac_address=mac_address or f"00:11:22:33:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}",
            hostname=hostname or f"host-{uuid.uuid4().hex[:4]}",
            ip_address=ip_address,
            is_active=is_active,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建白名单"""
        whitelists = []
        for i in range(count):
            whitelists.append(WhiteListFactory.create(**kwargs))
        return whitelists


class PXEServerStatusFactory:
    """PXE服务器状态工厂"""

    @staticmethod
    def create(name=None, status="online", ip_address=None, **kwargs):
        """创建PXE服务器状态"""
        from backend.models.osdeploy.pxe_server_status import PXEServerStatus
        return PXEServerStatus.objects.create(
            name=name or f"pxe-server-{uuid.uuid4().hex[:4]}",
            status=status,
            ip_address=ip_address or f"192.168.1.{10 + uuid.uuid4().int % 200}",
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建PXE服务器"""
        servers = []
        for i in range(count):
            servers.append(PXEServerStatusFactory.create(**kwargs))
        return servers
