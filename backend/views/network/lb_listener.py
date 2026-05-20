"""LBListener 视图集"""
from rest_framework.permissions import IsAuthenticated

from backend.models.network import LBListener
from backend.serializers.network import (
    LBListenerSerializer,
    LBListenerListSerializer,
    LBListenerCreateSerializer,
    LBListenerUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class LBListenerViewSet(UnifiedModelViewSet):
    """监听器视图集"""
    queryset = LBListener.objects.select_related('loadbalancer').all().order_by('id')
    serializer_class = LBListenerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['loadbalancer', 'protocol']
    search_fields = ['name']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return LBListenerCreateSerializer
        if self.action in ('update', 'partial_update'):
            return LBListenerUpdateSerializer
        if self.action == 'list':
            return LBListenerListSerializer
        return LBListenerSerializer