"""Safeguard 主机信息相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.host import Host
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet
from backend.services.safeguard import HostInfoService


class HostInfoViewSet(viewsets.ViewSet):
    """主机信息视图集"""
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=['get'], url_path='system-info')
    def system_info(self, request):
        """获取主机系统信息"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        try:
            host_id = int(host_id)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_id must be an integer')

        result = HostInfoService.get_system_info(host_id)
        if result['success']:
            return SuccessResponse(result['data'])
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取系统信息失败'))

    @action(detail=False, methods=['get'], url_path='ports-info')
    def ports_info(self, request):
        """获取主机端口信息"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        try:
            host_id = int(host_id)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_id must be an integer')

        result = HostInfoService.get_ports_info(host_id)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取端口信息失败'))

    @action(detail=False, methods=['get'], url_path='processes-info')
    def processes_info(self, request):
        """获取主机进程信息"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        try:
            host_id = int(host_id)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_id must be an integer')

        result = HostInfoService.get_processes_info(host_id)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取进程信息失败'))

    @action(detail=False, methods=['get'], url_path='services-info')
    def services_info(self, request):
        """获取主机服务信息"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        try:
            host_id = int(host_id)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_id must be an integer')

        result = HostInfoService.get_services_info(host_id)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取服务信息失败'))

    @action(detail=False, methods=['get'], url_path='accounts-info')
    def accounts_info(self, request):
        """获取主机系统账户信息"""
        host_id = request.query_params.get('host_id')
        if not host_id:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id is required')

        try:
            host_id = int(host_id)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_id must be an integer')

        result = HostInfoService.get_accounts_info(host_id)
        if result['success']:
            return SuccessResponse(result)
        return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result.get('error', '获取账户信息失败'))
