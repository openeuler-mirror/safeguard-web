"""PXEServerStatus 视图集"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from backend.models.osdeploy import PXEServerStatus
from backend.serializers.osdeploy import (
    PXEServerStatusSerializer,
    PXEServerStatusListSerializer,
    PXEServerStatusCreateSerializer,
    PXEServerStatusUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class PXEServerStatusViewSet(UnifiedModelViewSet):
    """PXE服务器状态视图集"""
    queryset = PXEServerStatus.objects.all().order_by('id')
    serializer_class = PXEServerStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['server_ip', 'status']
    search_fields = ['server_ip']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return PXEServerStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return PXEServerStatusUpdateSerializer
        if self.action == 'list':
            return PXEServerStatusListSerializer
        return PXEServerStatusSerializer