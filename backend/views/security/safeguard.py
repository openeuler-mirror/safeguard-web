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

    @action(['post'], False)
    def deploy(self, request, pk=None):
        """执行部署"""
        safeguard = self.get_object()
        success = SafeguardService.deploy(safeguard.id)
        if success:
            return self.success_response(data={'message': '部署任务已启动'})
        return self.error_response(code=7001, message='启动部署失败')

    @action(['post'], False)
    def rollback(self, request, pk=None):
        """回滚部署"""
        safeguard = self.get_object()
        success = SafeguardService.rollback(safeguard.id)
        if success:
            return self.success_response(data={'message': '回滚任务已启动'})
        return self.error_response(code=7002, message='启动回滚失败')