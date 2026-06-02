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

# ---------- Phase 3 新增：Network LB 扩展功能 ----------
from rest_framework.decorators import action
from backend.common import SuccessResponse, ErrorResponse


class LBExtensionMixin:
    """LB 扩展功能 Mixin"""

    @action(detail=False, methods=['get'], url_path='by_project')
    def by_project(self, request):
        """按项目查询 LB（placeholder，需对接外部系统）"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return ErrorResponse(400, errmsg='project_id is required')
        # TODO: 对接外部项目系统
        lbs = LoadBalancer.objects.all()
        serializer = LoadBalancerListSerializer(lbs, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=False, methods=['get'], url_path='by_k8s')
    def by_k8s(self, request):
        """按 K8s 集群查询 LB（placeholder，需对接外部系统）"""
        k8s_cluster = request.query_params.get('k8s_cluster')
        if not k8s_cluster:
            return ErrorResponse(400, errmsg='k8s_cluster is required')
        # TODO: 对接 K8s 集群信息
        lbs = LoadBalancer.objects.all()
        serializer = LoadBalancerListSerializer(lbs, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=False, methods=['get'], url_path='az_names')
    def az_names(self, request):
        """获取可用区名称列表（placeholder）"""
        # TODO: 对接外部 AZ 信息
        az_names = ["AZ-1", "AZ-2", "AZ-3"]
        return SuccessResponse(az_names)


LoadBalancerViewSet.by_project = LBExtensionMixin.by_project
LoadBalancerViewSet.by_k8s = LBExtensionMixin.by_k8s
LoadBalancerViewSet.az_names = LBExtensionMixin.az_names
