"""Safeguard 部署视图集"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from backend.models.security import SafeguardDeploy
from backend.serializers.security import (
    SafeguardDeploySerializer,
    SafeguardDeployListSerializer,
    SafeguardDeployCreateSerializer,
    SafeguardDeployUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet
from backend.common import SuccessResponse, ErrorResponse
from backend.services.security import SafeguardService


class SafeguardViewSet(UnifiedModelViewSet):
    """Safeguard 部署视图集"""
    queryset = SafeguardDeploy.objects.all().order_by('-id')
    serializer_class = SafeguardDeploySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'status', 'safeguard_type']
    search_fields = ['name', 'host']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return SafeguardDeployCreateSerializer
        if self.action in ('update', 'partial_update'):
            return SafeguardDeployUpdateSerializer
        if self.action == 'list':
            return SafeguardDeployListSerializer
        return SafeguardDeploySerializer

    @action(['post'], True)
    def deploy(self, request, pk=None):
        """执行部署"""
        safeguard = self.get_object()
        success = SafeguardService.deploy(safeguard.id)
        if success:
            return SuccessResponse({'message': '部署任务已启动'})
        return ErrorResponse(7001, errmsg='启动部署失败')

    @action(['post'], True)
    def rollback(self, request, pk=None):
        """回滚部署"""
        safeguard = self.get_object()
        success = SafeguardService.rollback(safeguard.id)
        if success:
            return SuccessResponse({'message': '回滚任务已启动'})
        return ErrorResponse(7002, errmsg='启动回滚失败')

    @action(['get'], True)
    def status(self, request, pk=None):
        """获取部署状态（含 Task 进度）"""
        safeguard = self.get_object()
        status_info = SafeguardService.get_deploy_status(safeguard.id)
        if status_info:
            return SuccessResponse(status_info)
        return ErrorResponse(7003, errmsg='获取状态失败')