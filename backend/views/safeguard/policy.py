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
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet, ServiceError
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
        serializer.save(created_by_id=self.request.user.id)


class HostSafeguardPolicyViewSet(UnifiedModelViewSet):
    """主机安全策略视图集"""
    queryset = HostSafeguardPolicy.objects.select_related('host', 'template').all().order_by('-created_at')
    serializer_class = HostSafeguardPolicySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'template', 'status']
    ordering_fields = ['created_at', 'id']

    def get_queryset(self):
        queryset = HostSafeguardPolicy.objects.select_related('host', 'template').all().order_by('-created_at')
        return queryset

    @action(detail=False, methods=['post'], url_path='bind')
    def bind(self, request):
        """为主机绑定策略"""
        host_id = request.data.get('host_id')
        template_id = request.data.get('template_id')

        if not host_id or not template_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id and template_id are required')

        try:
            result = PolicyService.bind_host_policy(host_id, template_id, created_by_id=request.user.id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @action(detail=True, methods=['get'], url_path='detail')
    def detail(self, request, pk=None):
        """获取主机策略详情"""
        try:
            result = PolicyService.get_host_policy(pk)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)


class PolicyApplyTaskViewSet(UnifiedModelViewSet):
    """策略下发任务视图集"""
    queryset = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').all().order_by('-created_at')
    serializer_class = PolicyApplyTaskSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['host', 'policy', 'task_type', 'status']
    ordering_fields = ['created_at', 'id']

    def get_queryset(self):
        queryset = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').all().order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.request.user.id)

    @action(detail=True, methods=['post'], url_path='apply')
    def apply(self, request, pk=None):
        """执行策略下发"""
        try:
            result = PolicyService.apply_policy(pk)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @action(detail=True, methods=['get'], url_path='status')
    def task_status(self, request, pk=None):
        """获取任务状态"""
        try:
            result = PolicyService.get_task_status(pk)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)
