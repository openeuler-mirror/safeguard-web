"""OutIpSN 视图集"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import OutIpSN
from backend.serializers.osdeploy import (
    OutIpSNSerializer,
    OutIpSNListSerializer,
    OutIpSNCreateSerializer,
    OutIpSNUpdateSerializer,
)
from backend.common import UnifiedModelViewSet


class OutIpSNViewSet(UnifiedModelViewSet):
    """出口IP序列号视图集"""
    queryset = OutIpSN.objects.all().order_by('id')
    serializer_class = OutIpSNSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['mac_address', 'sn']
    search_fields = ['mac_address', 'sn']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return OutIpSNCreateSerializer
        if self.action in ('update', 'partial_update'):
            return OutIpSNUpdateSerializer
        if self.action == 'list':
            return OutIpSNListSerializer
        return OutIpSNSerializer
