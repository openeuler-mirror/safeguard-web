"""WhiteList 视图集"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import WhiteList
from backend.serializers.osdeploy import (
    WhiteListSerializer,
    WhiteListListSerializer,
    WhiteListCreateSerializer,
    WhiteListUpdateSerializer,
)
from backend.common import UnifiedModelViewSet


class WhiteListViewSet(UnifiedModelViewSet):
    """MAC地址白名单视图集"""
    queryset = WhiteList.objects.all().order_by('id')
    serializer_class = WhiteListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['mac_address', 'hostname', 'ip_address', 'is_active']
    search_fields = ['mac_address', 'hostname', 'ip_address']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return WhiteListCreateSerializer
        if self.action in ('update', 'partial_update'):
            return WhiteListUpdateSerializer
        if self.action == 'list':
            return WhiteListListSerializer
        return WhiteListSerializer
