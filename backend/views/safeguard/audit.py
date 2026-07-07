"""Safeguard 审计相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.audit.audit_log import AuditLog
from backend.models.audit.system_log import SystemLog
from backend.models.host import Host
from backend.serializers.safeguard.audit import AuditLogSerializer, SystemLogSerializer
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet


class AuditLogViewSet(UnifiedModelViewSet):
    """审计日志视图集"""
    queryset = AuditLog.objects.select_related('user').all().order_by('-created_at')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['user', 'action', 'resource_type', 'status']
    search_fields = ['resource_name', 'action_details']
    ordering_fields = ['created_at', 'id']

    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').all().order_by('-created_at')
        return queryset


class SystemLogViewSet(UnifiedModelViewSet):
    """系统日志视图集"""
    queryset = SystemLog.objects.select_related('host').all().order_by('-timestamp')
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'source', 'level']
    search_fields = ['message']
    ordering_fields = ['timestamp', 'id']

    def get_queryset(self):
        queryset = SystemLog.objects.select_related('host').all().order_by('-timestamp')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)
