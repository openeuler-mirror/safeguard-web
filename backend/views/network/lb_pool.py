"""LBPool 视图集"""
from rest_framework.permissions import IsAuthenticated

from backend.models.network import LBPool
from backend.serializers.network import (
    LBPoolSerializer,
    LBPoolListSerializer,
    LBPoolCreateSerializer,
    LBPoolUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class LBPoolViewSet(UnifiedModelViewSet):
    """后端池视图集"""
    queryset = LBPool.objects.select_related('loadbalancer').all().order_by('id')
    serializer_class = LBPoolSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['loadbalancer', 'protocol']
    search_fields = ['name']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return LBPoolCreateSerializer
        if self.action in ('update', 'partial_update'):
            return LBPoolUpdateSerializer
        if self.action == 'list':
            return LBPoolListSerializer
        return LBPoolSerializer