"""LoadBalancer 视图集"""
from rest_framework.permissions import IsAuthenticated

from backend.models.network import LoadBalancer
from backend.serializers.network import (
    LoadBalancerSerializer,
    LoadBalancerListSerializer,
    LoadBalancerCreateSerializer,
    LoadBalancerUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet


class LoadBalancerViewSet(UnifiedModelViewSet):
    """负载均衡器视图集"""
    queryset = LoadBalancer.objects.all().order_by('id')
    serializer_class = LoadBalancerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'status', 'algorithm']
    search_fields = ['name', 'vip_address']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return LoadBalancerCreateSerializer
        if self.action in ('update', 'partial_update'):
            return LoadBalancerUpdateSerializer
        if self.action == 'list':
            return LoadBalancerListSerializer
        return LoadBalancerSerializer