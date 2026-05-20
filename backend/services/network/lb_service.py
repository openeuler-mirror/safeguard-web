"""负载均衡器服务"""
from typing import Optional, List
from backend.models.network import LoadBalancer, LBListener


class LBService:
    """负载均衡器服务"""

    @staticmethod
    def list_lbs(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取负载均衡器列表（支持分页和过滤）"""
        queryset = LoadBalancer.objects.all()
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
    def get_lb(lb_id: int) -> Optional[LoadBalancer]:
        """获取负载均衡器详情"""
        try:
            return LoadBalancer.objects.get(pk=lb_id)
        except LoadBalancer.DoesNotExist:
            return None

    @staticmethod
    def create_lb(data: dict) -> LoadBalancer:
        """创建负载均衡器"""
        lb = LoadBalancer.objects.create(
            name=data.get('name'),
            vip_address=data.get('vip_address'),
            port=data.get('port', 80),
            algorithm=data.get('algorithm', 'round_robin'),
            status=data.get('status', 'active'),
            description=data.get('description', ''),
        )
        return lb

    @staticmethod
    def update_lb(lb_id: int, data: dict) -> Optional[LoadBalancer]:
        """更新负载均衡器"""
        try:
            lb = LoadBalancer.objects.get(pk=lb_id)
            if 'name' in data:
                lb.name = data['name']
            if 'vip_address' in data:
                lb.vip_address = data['vip_address']
            if 'port' in data:
                lb.port = data['port']
            if 'algorithm' in data:
                lb.algorithm = data['algorithm']
            if 'status' in data:
                lb.status = data['status']
            if 'description' in data:
                lb.description = data['description']
            lb.save()
            return lb
        except LoadBalancer.DoesNotExist:
            return None

    @staticmethod
    def delete_lb(lb_id: int) -> bool:
        """删除负载均衡器"""
        try:
            lb = LoadBalancer.objects.get(pk=lb_id)
            lb.delete()
            return True
        except LoadBalancer.DoesNotExist:
            return False

    @staticmethod
    def get_listeners(lb_id: int) -> List[LBListener]:
        """获取负载均衡器的监听器列表"""
        try:
            lb = LoadBalancer.objects.get(pk=lb_id)
            return list(lb.listeners.all())
        except LoadBalancer.DoesNotExist:
            return []