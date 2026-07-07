"""Safeguard 文件监控相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.safeguard.file_monitor import (
    FileMonitorRule,
    FileMonitorEvent,
)
from backend.models.host import Host
from backend.serializers.safeguard.file_monitor import (
    FileMonitorRuleSerializer,
    FileMonitorRuleCreateSerializer,
    FileMonitorRuleUpdateSerializer,
    FileMonitorEventSerializer,
)
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet
from backend.services.safeguard import AuditService


class FileMonitorRuleViewSet(UnifiedModelViewSet):
    """文件监控规则视图集"""
    queryset = FileMonitorRule.objects.select_related('host').all().order_by('-created_at')
    serializer_class = FileMonitorRuleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'enabled', 'monitor_type']
    search_fields = ['path']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return FileMonitorRuleCreateSerializer
        if self.action in ['update', 'partial_update']:
            return FileMonitorRuleUpdateSerializer
        return FileMonitorRuleSerializer

    def get_queryset(self):
        queryset = FileMonitorRule.objects.select_related('host').all().order_by('-created_at')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'], url_path='collect-events')
    def collect_events(self, request):
        """收集文件监控事件"""
        host_id = request.data.get('host_id')

        result = AuditService.collect_file_events(host_id)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '收集文件监控事件失败'))

    @action(detail=True, methods=['post'], url_path='start-monitor')
    def start_monitor(self, request, pk=None):
        """启用监控规则"""
        try:
            rule = self.get_object()
            rule.enabled = True
            rule.save()
            return SuccessResponse({'id': rule.id, 'enabled': True})
        except FileMonitorRule.DoesNotExist:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg='监控规则不存在')

    @action(detail=True, methods=['post'], url_path='stop-monitor')
    def stop_monitor(self, request, pk=None):
        """禁用监控规则"""
        try:
            rule = self.get_object()
            rule.enabled = False
            rule.save()
            return SuccessResponse({'id': rule.id, 'enabled': False})
        except FileMonitorRule.DoesNotExist:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg='监控规则不存在')


class FileMonitorEventViewSet(UnifiedModelViewSet):
    """文件监控事件视图集"""
    queryset = FileMonitorEvent.objects.select_related('host', 'rule').all().order_by('-timestamp')
    serializer_class = FileMonitorEventSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'rule', 'event_type']
    ordering_fields = ['timestamp', 'id']

    def get_queryset(self):
        queryset = FileMonitorEvent.objects.select_related('host', 'rule').all().order_by('-timestamp')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)
