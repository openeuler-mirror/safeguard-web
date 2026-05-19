"""健康检查服务"""
from typing import Optional
from backend.models.network import LBHealthMonitor, LBPool


class HealthMonitorService:
    """健康检查服务"""

    @staticmethod
    def list_monitors(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取健康检查列表（支持分页和过滤）"""
        queryset = LBHealthMonitor.objects.select_related('pool').all()
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
    def get_monitor(monitor_id: int) -> Optional[LBHealthMonitor]:
        """获取健康检查详情"""
        try:
            return LBHealthMonitor.objects.select_related('pool').get(pk=monitor_id)
        except LBHealthMonitor.DoesNotExist:
            return None

    @staticmethod
    def create_monitor(pool_id: int, data: dict) -> Optional[LBHealthMonitor]:
        """创建健康检查"""
        try:
            pool = LBPool.objects.get(pk=pool_id)
        except LBPool.DoesNotExist:
            return None

        monitor = LBHealthMonitor.objects.create(
            pool=pool,
            monitor_type=data.get('monitor_type'),
            interval=data.get('interval', 5),
            timeout=data.get('timeout', 3),
            retry=data.get('retry', 3),
            description=data.get('description', ''),
        )
        return monitor

    @staticmethod
    def update_monitor(monitor_id: int, data: dict) -> Optional[LBHealthMonitor]:
        """更新健康检查"""
        try:
            monitor = LBHealthMonitor.objects.get(pk=monitor_id)
            if 'monitor_type' in data:
                monitor.monitor_type = data['monitor_type']
            if 'interval' in data:
                monitor.interval = data['interval']
            if 'timeout' in data:
                monitor.timeout = data['timeout']
            if 'retry' in data:
                monitor.retry = data['retry']
            if 'description' in data:
                monitor.description = data['description']
            monitor.save()
            return monitor
        except LBHealthMonitor.DoesNotExist:
            return None

    @staticmethod
    def delete_monitor(monitor_id: int) -> bool:
        """删除健康检查"""
        try:
            monitor = LBHealthMonitor.objects.get(pk=monitor_id)
            monitor.delete()
            return True
        except LBHealthMonitor.DoesNotExist:
            return False

    @staticmethod
    def get_monitor_by_pool(pool_id: int) -> Optional[LBHealthMonitor]:
        """根据后端池获取健康检查"""
        try:
            return LBHealthMonitor.objects.get(pool_id=pool_id)
        except LBHealthMonitor.DoesNotExist:
            return None