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
