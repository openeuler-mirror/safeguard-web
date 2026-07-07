"""Safeguard 审计相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.audit.audit_log import AuditLog
from backend.serializers.safeguard.audit import AuditLogSerializer
from backend.permissions.authority import IsAdmin
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
