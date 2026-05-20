"""LBHealthMonitor 视图集"""
from rest_framework.permissions import IsAuthenticated

from backend.models.network import LBHealthMonitor
from backend.serializers.network import (
    LBHealthMonitorSerializer,
    LBHealthMonitorListSerializer,
    LBHealthMonitorCreateSerializer,
    LBHealthMonitorUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class LBHealthMonitorViewSet(UnifiedModelViewSet):
    """健康检查视图集"""
    queryset = LBHealthMonitor.objects.select_related('pool').all().order_by('id')
    serializer_class = LBHealthMonitorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pool', 'monitor_type']
    search_fields = []
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return LBHealthMonitorCreateSerializer
        if self.action in ('update', 'partial_update'):
            return LBHealthMonitorUpdateSerializer
        if self.action == 'list':
            return LBHealthMonitorListSerializer
        return LBHealthMonitorSerializer