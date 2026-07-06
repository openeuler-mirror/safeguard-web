"""Safeguard 策略相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)
from backend.models.host import Host
from backend.serializers.safeguard.policy import (
    SafeguardPolicyTemplateSerializer,
    SafeguardPolicyTemplateCreateSerializer,
    SafeguardPolicyTemplateUpdateSerializer,
    HostSafeguardPolicySerializer,
    PolicyApplyTaskSerializer,
)
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet
from backend.services.safeguard import PolicyService


class SafeguardPolicyTemplateViewSet(UnifiedModelViewSet):
    """安全策略模板视图集"""
    queryset = SafeguardPolicyTemplate.objects.all().order_by('-created_at')
    serializer_class = SafeguardPolicyTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['template_type', 'is_builtin']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return SafeguardPolicyTemplateCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SafeguardPolicyTemplateUpdateSerializer
        return SafeguardPolicyTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HostSafeguardPolicyViewSet(UnifiedModelViewSet):
    """主机安全策略视图集"""
    queryset = HostSafeguardPolicy.objects.select_related('host', 'template').all().order_by('-created_at')
    serializer_class = HostSafeguardPolicySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'template', 'status']
    ordering_fields = ['created_at', 'id']

    def get_queryset(self):
        queryset = HostSafeguardPolicy.objects.select_related('host', 'template').all().order_by('-created_at')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)

    @action(detail=False, methods=['post'], url_path='bind')
    def bind(self, request):
        """为主机绑定策略"""
        host_id = request.data.get('host_id')
        template_id = request.data.get('template_id')

        if not host_id or not template_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id and template_id are required')

        result = PolicyService.bind_host_policy(host_id, template_id, created_by=request.user)
        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '绑定失败'))

    @action(detail=True, methods=['get'], url_path='detail')
    def detail(self, request, pk=None):
        """获取主机策略详情"""
        result = PolicyService.get_host_policy(pk)
        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取失败'))


class PolicyApplyTaskViewSet(UnifiedModelViewSet):
    """策略下发任务视图集"""
    queryset = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').all().order_by('-created_at')
    serializer_class = PolicyApplyTaskSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'policy', 'task_type', 'status']
    ordering_fields = ['created_at', 'id']

    def get_queryset(self):
        queryset = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').all().order_by('-created_at')
        return DataScopePermission.filter_queryset(queryset, self.request.user.id, Host)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='apply')
    def apply(self, request, pk=None):
        """执行策略下发"""
        result = PolicyService.apply_policy(pk)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '策略下发失败'))

    @action(detail=True, methods=['get'], url_path='status')
    def task_status(self, request, pk=None):
        """获取任务状态"""
        result = PolicyService.get_task_status(pk)
        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取任务状态失败'))
