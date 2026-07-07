"""Safeguard 监控相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)

from backend.models.safeguard.monitor import HostMonitorData
from backend.models.host import Host
from backend.serializers.safeguard.monitor import HostMonitorDataSerializer
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet
from backend.services.safeguard import MonitorService


class HostMonitorDataViewSet(UnifiedModelViewSet):
    """主机监控数据视图集"""
    queryset = HostMonitorData.objects.select_related('host').all().order_by('-timestamp')
    serializer_class = HostMonitorDataSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host']
    ordering_fields = ['timestamp', 'id']

    def get_queryset(self):
        queryset = HostMonitorData.objects.select_related('host').all().order_by('-timestamp')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)

    @action(detail=False, methods=['post'], url_path='collect')
    def collect(self, request):
        """采集主机监控数据"""
        host_id = request.data.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        result = MonitorService.collect_all_metrics(host_id, save=True)
        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '采集失败'))

    @action(detail=False, methods=['post'], url_path='batch_collect')
    def batch_collect(self, request):
        """批量采集主机监控数据"""
        host_ids = request.data.get('host_ids', [])
        if not host_ids:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_ids is required')

        results = []
        for host_id in host_ids:
            result = MonitorService.collect_all_metrics(host_id, save=True)
            results.append({
                'host_id': host_id,
                'success': result['success'],
                'error': result.get('error'),
            })

        return SuccessResponse({'results': results})

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """获取监控历史数据"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        metric_type = request.query_params.get('metric_type')

        # 安全解析分页参数
        try:
            page = int(request.query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1
        # 确保 page >= 1
        if page < 1:
            page = 1

        try:
            page_size = int(request.query_params.get('page_size', 100))
        except (ValueError, TypeError):
            page_size = 100
        # 确保 page_size 在合理范围内 (1-1000)
        if page_size < 1:
            page_size = 100
        if page_size > 1000:
            page_size = 1000

        # 解析时间参数
        from datetime import datetime
        start_datetime = None
        end_datetime = None

        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                pass

        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                pass

        result = MonitorService.get_monitor_history(
            host_id,
            start_time=start_datetime,
            end_time=end_datetime,
            metric_type=metric_type,
            page=page,
            page_size=page_size
        )

        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '查询失败'))

    @action(detail=True, methods=['get'], url_path='latest')
    def latest(self, request, pk=None):
        """获取主机最新监控数据"""
        try:
            host = Host.objects.get(id=pk)
        except Host.DoesNotExist:
            return ErrorResponse(ErrCode.HOST_NOT_FOUND, errmsg='主机不存在')

        latest_data = HostMonitorData.objects.filter(host=host).order_by('-timestamp').first()
        if latest_data:
            serializer = HostMonitorDataSerializer(latest_data)
            return SuccessResponse(serializer.data)
        return SuccessResponse(None, errmsg='暂无监控数据')
