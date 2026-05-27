"""主机相关视图集"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

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
from backend.common import ErrCode, SuccessResponse, ErrorResponse, UnifiedModelViewSet
from backend.services.host import ClusterService, HostService, VMService


class ClusterViewSet(UnifiedModelViewSet):
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
            return ErrorResponse(ErrCode.CLUSTER_HAS_HOSTS)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='hosts')
    def hosts(self, request, pk=None):
        """获取集群关联的主机列表"""
        cluster = self.get_object()
        hosts = cluster.host_set.all()
        serializer = HostListSerializer(hosts, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=True, methods=['get'], url_path='topology')
    def topology(self, request, pk=None):
        """获取集群拓扑"""
        topology = ClusterService.get_cluster_topology(pk)
        if topology is None:
            return ErrorResponse(ErrCode.CLUSTER_NOT_FOUND)
        return SuccessResponse(topology)

    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request):
        """获取集群树（用于下拉选择）"""
        clusters = Cluster.objects.all().order_by('id')
        data = [{'id': c.id, 'name': c.name, 'label': c.name} for c in clusters]
        return SuccessResponse(data)


class HostViewSet(UnifiedModelViewSet):
    """主机管理视图集"""
    queryset = Host.objects.select_related('cluster').all().order_by('id')
    serializer_class = HostSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['hostname', 'ip_address', 'status', 'cluster', 'host_type']
    search_fields = ['hostname', 'ip_address', 'serial_number']
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
        result = HostService.collect_hardware(pk)
        if result['success']:
            return SuccessResponse(result['data'], errmsg=result['message'])
        return ErrorResponse(ErrCode.HOST_HARDWARE_COLLECT_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='collect_lldp')
    def collect_lldp(self, request, pk=None):
        """采集 LLDP 拓扑信息"""
        result = HostService.collect_lldp(pk)
        if result['success']:
            return SuccessResponse(result['data'], errmsg=result['message'])
        return ErrorResponse(ErrCode.HOST_LLDP_COLLECT_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='collect_all')
    def collect_all(self, request, pk=None):
        """采集主机所有硬件信息（包括 LLDP）"""
        result = HostService.collect_all(pk)
        if result['success']:
            return SuccessResponse(result['data'], errmsg=result['message'])
        return ErrorResponse(ErrCode.HOST_HARDWARE_COLLECT_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='update_password')
    def update_password(self, request, pk=None):
        """修改主机密码"""
        new_password = request.data.get('password')
        key = request.data.get('key', 'culinux')
        result = HostService.update_host_password(pk, new_password, key)
        if result['success']:
            return SuccessResponse({'password': result['password']}, errmsg=result['message'])
        return ErrorResponse(ErrCode.HOST_PASSWORD_UPDATE_FAILED, errmsg=result['message'])


class VMViewSet(UnifiedModelViewSet):
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
        result = VMService.start_vm(pk)
        if result['success']:
            return SuccessResponse(errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='stop')
    def stop(self, request, pk=None):
        """停止VM"""
        result = VMService.stop_vm(pk)
        if result['success']:
            return SuccessResponse(errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='reboot')
    def reboot(self, request, pk=None):
        """重启VM"""
        result = VMService.reboot_vm(pk)
        if result['success']:
            return SuccessResponse(errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='pause')
    def pause(self, request, pk=None):
        """暂停VM"""
        result = VMService.pause_vm(pk)
        if result['success']:
            return SuccessResponse(errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['post'], url_path='resume')
    def resume(self, request, pk=None):
        """恢复VM"""
        result = VMService.resume_vm(pk)
        if result['success']:
            return SuccessResponse(errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=result['message'])

    @action(detail=True, methods=['get'], url_path='status')
    def status(self, request, pk=None):
        """获取VM状态"""
        result = VMService.get_vm_status(pk)
        if result['success']:
            return SuccessResponse({'status': result['status']}, errmsg=result['message'])
        return ErrorResponse(ErrCode.VM_NOT_FOUND, errmsg=result['message'])