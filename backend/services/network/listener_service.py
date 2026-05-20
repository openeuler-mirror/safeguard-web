"""监听器服务"""
from typing import Optional, List
from backend.models.network import LBListener, LoadBalancer


class ListenerService:
    """监听器服务"""

    @staticmethod
    def list_listeners(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取监听器列表（支持分页和过滤）"""
        queryset = LBListener.objects.select_related('loadbalancer').all()
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
    def get_listener(listener_id: int) -> Optional[LBListener]:
        """获取监听器详情"""
        try:
            return LBListener.objects.select_related('loadbalancer').get(pk=listener_id)
        except LBListener.DoesNotExist:
            return None

    @staticmethod
    def create_listener(lb_id: int, data: dict) -> Optional[LBListener]:
        """创建监听器"""
        try:
            lb = LoadBalancer.objects.get(pk=lb_id)
        except LoadBalancer.DoesNotExist:
            return None

        listener = LBListener.objects.create(
            loadbalancer=lb,
            protocol=data.get('protocol'),
            port=data.get('port'),
            name=data.get('name', ''),
            description=data.get('description', ''),
        )
        return listener

    @staticmethod
    def update_listener(listener_id: int, data: dict) -> Optional[LBListener]:
        """更新监听器"""
        try:
            listener = LBListener.objects.get(pk=listener_id)
            if 'protocol' in data:
                listener.protocol = data['protocol']
            if 'port' in data:
                listener.port = data['port']
            if 'name' in data:
                listener.name = data['name']
            if 'description' in data:
                listener.description = data['description']
            listener.save()
            return listener
        except LBListener.DoesNotExist:
            return None

    @staticmethod
    def delete_listener(listener_id: int) -> bool:
        """删除监听器"""
        try:
            listener = LBListener.objects.get(pk=listener_id)
            listener.delete()
            return True
        except LBListener.DoesNotExist:
            return False