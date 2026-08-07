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
    def create(server_ip=None, interface="eth0", dhcp_range_start=None, dhcp_range_end=None,
               subnet=None, gateway=None, status="active", **kwargs):
        """创建PXE服务器状态"""
        base_ip = 100 + uuid.uuid4().int % 100
        return PXEServerStatus.objects.create(
            server_ip=server_ip or f"192.168.1.{base_ip}",
            interface=interface,
            dhcp_range_start=dhcp_range_start or f"192.168.1.{base_ip + 10}",
            dhcp_range_end=dhcp_range_end or f"192.168.1.{base_ip + 50}",
            subnet=subnet or "255.255.255.0",
            gateway=gateway or "192.168.1.1",
            status=status,
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建PXE服务器"""
        servers = []
        for i in range(count):
            servers.append(PXEServerStatusFactory.create(**kwargs))
        return servers


class KickStartFileStatusFactory:
    """Kickstart文件状态工厂"""

    @staticmethod
    def create(name=None, content=None, repo=None, kernel_options=None, **kwargs):
        """创建Kickstart文件状态"""
        return KickStartFileStatus.objects.create(
            name=name or f"kickstart-{uuid.uuid4().hex[:4]}",
            content=content or "# Kickstart config\ninstall\ntext",
            repo=repo,
            kernel_options=kernel_options or {},
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建Kickstart文件"""
        files = []
        for i in range(count):
            files.append(KickStartFileStatusFactory.create(**kwargs))
        return files


class ISOFileStatusFactory:
    """ISO文件状态工厂"""

    @staticmethod
    def create(filename=None, size=None, md5sum=None, status="available", file_path=None, **kwargs):
        """创建ISO文件状态"""
        return ISOFileStatus.objects.create(
            filename=filename or f"os-{uuid.uuid4().hex[:6]}.iso",
            size=size or 1024 * 1024 * 1024,  # 1GB
            md5sum=md5sum or uuid.uuid4().hex,
            status=status,
            file_path=file_path or f"/isos/{uuid.uuid4().hex[:8]}.iso",
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建ISO文件"""
        isos = []
        for i in range(count):
            isos.append(ISOFileStatusFactory.create(**kwargs))
        return isos


class OutIpSNFactory:
    """输出IP和序列号工厂"""

    @staticmethod
    def create(mac_address=None, sn=None, **kwargs):
        """创建输出IP和序列号"""
        return OutIpSN.objects.create(
            mac_address=mac_address or f"00:11:22:33:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}",
            sn=sn or f"SN{uuid.uuid4().hex[:8].upper()}",
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建"""
        items = []
        for i in range(count):
            items.append(OutIpSNFactory.create(**kwargs))
        return items


class SensorDataFactory:
    """传感器数据工厂"""

    @staticmethod
    def create(ip=None, function=None, data=None, time=None, **kwargs):
        """创建传感器数据"""
        return SensorData.objects.create(
            ip=ip or f"192.168.1.{100 + uuid.uuid4().int % 100}",
            function=function or "hardware_scan",
            data=data or '{"temperature": 25}',
            time=time or "2024-01-01 12:00:00",
            **kwargs
        )

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建传感器数据"""
        data_list = []
        for i in range(count):
            data_list.append(SensorDataFactory.create(**kwargs))
        return data_list
