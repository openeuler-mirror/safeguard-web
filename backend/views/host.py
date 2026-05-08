"""主机相关视图集"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.models.host import Cluster, Host, VM
from backend.serializers.host import (
    ClusterSerializer,
    ClusterCreateSerializer,
    ClusterUpdateSerializer,
    HostSerializer,
    HostCreateSerializer,
    HostUpdateSerializer,
    HostListSerializer,
    VMSerializer,
    VMCreateSerializer,
    VMUpdateSerializer,
    VMListSerializer,
)
from backend.permissions.authority import IsAdmin


class ClusterViewSet(viewsets.ModelViewSet):
    """集群管理视图集"""
    queryset = Cluster.objects.all().order_by('id')
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return ClusterCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ClusterUpdateSerializer
        return ClusterSerializer

    def destroy(self, request, *args, **kwargs):
        """删除集群前检查是否有主机关联"""
        cluster = self.get_object()
        if cluster.host_set.exists():
            return Response(
                {'error': '该集群下存在主机，无法删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='hosts')
    def hosts(self, request, pk=None):
        """获取集群关联的主机列表"""
        cluster = self.get_object()
        hosts = cluster.host_set.all()
        serializer = HostListSerializer(hosts, many=True)
        return Response(serializer.data)

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


class HostViewSet(viewsets.ModelViewSet):
    """主机管理视图集"""
    queryset = Host.objects.select_related('cluster').all().order_by('id')
    serializer_class = HostSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['hostname', 'ip_address', 'status', 'cluster']
    search_fields = ['hostname', 'ip_address']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return HostCreateSerializer
        if self.action in ('update', 'partial_update'):
            return HostUpdateSerializer
        if self.action == 'list':
            return HostListSerializer
        return HostSerializer

    @action(detail=True, methods=['post'], url_path='collect_hardware')
    def collect_hardware(self, request, pk=None):
        """采集主机硬件信息"""
        host = self.get_object()
        # TODO: 调用 HostService.collect_hardware()
        return Response({'message': '硬件信息采集功能待实现'})


class VMViewSet(viewsets.ModelViewSet):
    """虚拟机管理视图集"""
    queryset = VM.objects.select_related('host', 'cluster').all().order_by('id')
    serializer_class = VMSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['name', 'uuid', 'status', 'host', 'cluster']
    search_fields = ['name', 'uuid', 'ip_address']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return VMCreateSerializer
        if self.action in ('update', 'partial_update'):
            return VMUpdateSerializer
        if self.action == 'list':
            return VMListSerializer
        return VMSerializer

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        """启动VM"""
        vm = self.get_object()
        # TODO: 调用 VMService.start_vm()
        return Response({'message': 'VM启动功能待实现'})

    @action(detail=True, methods=['post'], url_path='stop')
    def stop(self, request, pk=None):
        """停止VM"""
        vm = self.get_object()
        # TODO: 调用 VMService.stop_vm()
        return Response({'message': 'VM停止功能待实现'})

    @action(detail=True, methods=['post'], url_path='reboot')
    def reboot(self, request, pk=None):
        """重启VM"""
        vm = self.get_object()
        # TODO: 调用 VMService.reboot_vm()
        return Response({'message': 'VM重启功能待实现'})