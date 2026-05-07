"""主机相关视图集"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.models.host import Cluster
from backend.serializers.host import (
    ClusterSerializer,
    ClusterCreateSerializer,
    ClusterUpdateSerializer,
)
from backend.permissions.host import HostPermission


class ClusterViewSet(viewsets.ModelViewSet):
    """集群管理视图集"""
    queryset = Cluster.objects.all().order_by('id')
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, HostPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return ClusterCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ClusterUpdateSerializer
        return ClusterSerializer

    @action(detail=True, methods=['get'], url_path='topology')
    def topology(self, request, pk=None):
        """获取集群拓扑"""
        cluster = self.get_object()
        # TODO: 调用 ClusterService.get_cluster_topology()
        return Response({
            'message': '拓扑功能待实现',
            'cluster_id': cluster.id,
            'cluster_name': cluster.name
        })

    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request):
        """获取集群树（用于下拉选择）"""
        clusters = Cluster.objects.all().order_by('id')
        data = [{'id': c.id, 'name': c.name, 'label': c.name} for c in clusters]
        return Response(data)