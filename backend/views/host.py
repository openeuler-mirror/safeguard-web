"""主机相关视图集"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)

from backend.models.host import Cluster, Host, VM, Image
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
    ImageSerializer,
    ImageCreateSerializer,
    ImageUpdateSerializer,
)
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import ErrCode, SuccessResponse, ErrorResponse, UnifiedModelViewSet
from backend.services.host import ClusterService, HostService, VMService


class ClusterViewSet(UnifiedModelViewSet):
    """集群管理视图集"""
    queryset = Cluster.objects.all().order_by('id')
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Cluster.objects.all().order_by('id')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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



    @action(detail=False, methods=['post'], url_path='import')
    def import_hosts(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='please upload Excel file')
        result = HostService.import_hosts_from_excel(file_obj)
        if result['success']:
            return SuccessResponse(result, errmsg=result['message'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result['message'])

    @action(detail=False, methods=['get'], url_path='export')
    def export_hosts(self, request):
        from django.http import HttpResponse
        filters = {}
        if request.query_params.get('status'):
            filters['status'] = request.query_params.get('status')
        if request.query_params.get('cluster'):
            filters['cluster'] = request.query_params.get('cluster')
        data = HostService.export_hosts_to_excel(filters)
        response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="hosts.xlsx"'
        return response

    @action(detail=True, methods=['post'], url_path='remote_command')
    def remote_command(self, request, pk=None):
        command = request.data.get('command')
        if not command:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='command is required')
        result = HostService.remote_command(pk, command)
        if result['success']:
            return SuccessResponse(result, errmsg=result['message'])
        return ErrorResponse(ErrCode.HOST_CONNECTION_FAILED, errmsg=result['message'])

    @action(detail=False, methods=['post'], url_path='batch_update_password')
    def batch_update_password(self, request):
        host_ids = request.data.get('host_ids', [])
        new_password = request.data.get('password')
        key = request.data.get('key', 'culinux')
        if not host_ids:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_ids is required')
        result = HostService.batch_update_password(host_ids, new_password, key)
        if result['success']:
            return SuccessResponse(result, errmsg=result['message'])
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


class ImageViewSet(UnifiedModelViewSet):
    """镜像管理视图集"""
    queryset = Image.objects.select_related('host').all().order_by('id')
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return ImageCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ImageUpdateSerializer
        return ImageSerializer

    @action(detail=False, methods=['get'], url_path='list_by_host')
    def list_by_host(self, request):
        """根据主机获取镜像列表"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        images = Image.objects.filter(host_id=host_id)
        serializer = ImageSerializer(images, many=True)
        return SuccessResponse(serializer.data)

    @action(detail=True, methods=['post'], url_path='refresh')
    def refresh(self, request, pk=None):
        """从远程主机刷新镜像列表"""
        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg='镜像不存在')

        try:
            from backend.utils.ssh import SSHClient

            host = image.host
            client = SSHClient(
                host=host.ip_address,
                port=host.port,
                username=host.username,
                password=host.password,
            )
            if not client.connect():
                return ErrorResponse(ErrCode.HOST_CONNECTION_FAILED, errmsg='无法连接到主机')

            # 执行 ls 命令获取镜像列表
            stdout, stderr, exit_code = client.execute_command(f'ls -l {image.path}')
            client.close()

            if exit_code != 0:
                return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=stderr)

            # 解析输出，提取 .qcow2 文件
            import re
            import time
            import random

            image_list = []
            lines = stdout.split('\n')
            for line in lines:
                if '.qcow2' in line:
                    fields = line.split()
                    if len(fields) >= 9:
                        filename = fields[-1]
                        # 生成 ID：8位随机字符 + 时间戳
                        random_str = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(8))
                        image_id = f"{random_str}{int(time.time())}"

                        # 判断操作系统类型
                        filename_lower = filename.lower()
                        if 'centos' in filename_lower:
                            ostype = 'centos'
                        elif 'culinux' in filename_lower:
                            ostype = 'culinux'
                        elif 'openeuler' in filename_lower:
                            ostype = 'openeuler'
                        else:
                            ostype = 'unknown'

                        full_path = f"{image.path}/{filename}"
                        image_list.append({
                            'id': image_id,
                            'name': filename,
                            'ostype': ostype,
                            'path': full_path,
                            'host': host.id,
                        })

            # 批量创建镜像记录
            created_count = 0
            for img_data in image_list:
                _, created = Image.objects.get_or_create(
                    id=img_data['id'],
                    defaults={
                        'name': img_data['name'],
                        'ostype': img_data['ostype'],
                        'path': img_data['path'],
                        'host_id': img_data['host'],
                    }
                )
                if created:
                    created_count += 1

            return SuccessResponse({
                'total': len(image_list),
                'created': created_count,
            }, errmsg=f'成功刷新 {created_count} 个镜像')

        except ImportError:
            return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg='SSH 客户端未安装')
        except Exception as e:
            logger.error(f"Failed to refresh images: {e}")
            return ErrorResponse(ErrCode.VM_OPERATION_FAILED, errmsg=str(e))

