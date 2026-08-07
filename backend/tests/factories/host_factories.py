"""主机资产相关测试数据工厂"""
import uuid
from backend.models.host import Cluster, Host, VM, Image


class ClusterFactory:
    """集群工厂"""

    @staticmethod
    def create(name=None, description=None, **kwargs):
        """创建集群"""
        return Cluster.objects.create(
            name=name or f"cluster_{uuid.uuid4().hex[:8]}",
            description=description or "测试集群",
            **kwargs
        )

    @staticmethod
    def create_batch(count=3, **kwargs):
        """批量创建集群"""
        return [ClusterFactory.create(**kwargs) for _ in range(count)]


class HostFactory:
    """宿主机工厂"""

    @staticmethod
    def create(
        hostname=None,
        ip_address=None,
        port=22,
        username="root",
        password="password123",
        cluster=None,
        status="offline",
        host_type="VMHost",
        safeguard_status="uninstalled",
        monitor_enabled=False,
        **kwargs
    ):
        """创建宿主机"""
        if cluster is None:
            cluster = ClusterFactory.create()

        return Host.objects.create(
            hostname=hostname or f"host_{uuid.uuid4().hex[:8]}",
            ip_address=ip_address or f"192.168.{uuid.uuid4().int % 255}.{uuid.uuid4().int % 255}",
            port=port,
            username=username,
            password=password,
            cluster=cluster,
            status=status,
            host_type=host_type,
            safeguard_status=safeguard_status,
            monitor_enabled=monitor_enabled,
            **kwargs
        )

    @staticmethod
    def create_batch(count=5, cluster=None, **kwargs):
        """批量创建宿主机"""
        if cluster is None:
            cluster = ClusterFactory.create()
        return [HostFactory.create(cluster=cluster, **kwargs) for _ in range(count)]

    @staticmethod
    def create_with_vms(vm_count=2, **kwargs):
        """创建带有虚拟机的宿主机"""
        host = HostFactory.create(**kwargs)
        for _ in range(vm_count):
            VMFactory.create(host=host)
        return host


class VMFactory:
    """虚拟机工厂"""

    @staticmethod
    def create(
        name=None,
        uuid=None,
        host=None,
        status="stopped",
        vcpu=2,
        memory=4294967296,
        disk=107374182400,
        **kwargs
    ):
        """创建虚拟机"""
        if host is None:
            host = HostFactory.create()

        return VM.objects.create(
            name=name or f"vm_{uuid.uuid4().hex[:8]}",
            uuid=uuid or str(uuid.uuid4()),
            host=host,
            status=status,
            vcpu=vcpu,
            memory=memory,
            disk=disk,
            **kwargs
        )

    @staticmethod
    def create_batch(count=3, host=None, **kwargs):
        """批量创建虚拟机"""
        if host is None:
            host = HostFactory.create()
        return [VMFactory.create(host=host, **kwargs) for _ in range(count)]

