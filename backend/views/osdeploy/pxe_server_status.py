"""PXEServerStatus 视图集"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from backend.models.osdeploy import PXEServerStatus
from backend.serializers.osdeploy import (
    PXEServerStatusSerializer,
    PXEServerStatusListSerializer,
    PXEServerStatusCreateSerializer,
    PXEServerStatusUpdateSerializer,
)
from backend.common.viewsets import UnifiedModelViewSet
from backend.services.osdeploy.dhcp_service import DHCPService
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class PXEServerStatusViewSet(UnifiedModelViewSet):
    """PXE服务器状态视图集"""
    queryset = PXEServerStatus.objects.all().order_by('id')
    serializer_class = PXEServerStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['server_ip', 'status']
    search_fields = ['server_ip']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return PXEServerStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return PXEServerStatusUpdateSerializer
        if self.action == 'list':
            return PXEServerStatusListSerializer
        return PXEServerStatusSerializer

    @action(['post'], False)
    def start_dhcp(self, request):
        """启动DHCP服务"""
        result = DHCPService.start_dhcp_service()
        if result["status"] == "success":
            return SuccessResponse(result)
        return ErrorResponse(code=ErrCode.INTERNAL_ERROR, errmsg=result["message"])

    @action(['post'], False)
    def stop_dhcp(self, request):
        """停止DHCP服务"""
        result = DHCPService.stop_dhcp_service()
        if result["status"] == "success":
            return SuccessResponse(result)
        return ErrorResponse(code=ErrCode.INTERNAL_ERROR, errmsg=result["message"])

    @action(['post'], False)
    def restart_dhcp(self, request):
        """重启DHCP服务"""
        result = DHCPService.restart_dhcp_service()
        if result["status"] == "success":
            return SuccessResponse(result)
        return ErrorResponse(code=ErrCode.INTERNAL_ERROR, errmsg=result["message"])

    @action(['get'], False)
    def dhcp_status(self, request):
        """获取DHCP服务状态"""
        is_running = DHCPService.is_dhcp_running()
        return SuccessResponse({"is_running": is_running})