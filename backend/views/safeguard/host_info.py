"""Safeguard 主机信息相关视图集"""
import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from backend.models.host import Host
from backend.permissions.authority import IsAdmin
from backend.permissions.base import DataScopePermission
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet, ServiceError
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

        try:
            result = HostInfoService.get_system_info(host_id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

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

        try:
            result = HostInfoService.get_ports_info(host_id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

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

        try:
            result = HostInfoService.get_processes_info(host_id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

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

        try:
            result = HostInfoService.get_services_info(host_id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

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

        try:
            result = HostInfoService.get_accounts_info(host_id)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @action(detail=False, methods=['post'], url_path='service-control')
    def service_control(self, request):
        """控制主机服务（启动、停止、重启、重载、启用、禁用）"""
        host_id = request.data.get('host_id')
        service_name = request.data.get('service_name')
        action = request.data.get('action')

        if not host_id or not service_name or not action:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id, service_name and action are required')

        if action not in ['start', 'stop', 'restart', 'reload', 'enable', 'disable']:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='Invalid action')

        try:
            result = HostInfoService.control_service(host_id, service_name, action)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @action(detail=False, methods=['get'], url_path='service-logs')
    def service_logs(self, request):
        """获取服务日志"""
        host_id = request.query_params.get('host_id')
        service_name = request.query_params.get('service_name')
        lines = request.query_params.get('lines', 100)

        if not host_id or not service_name:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id and service_name are required')

        try:
            lines = int(lines)
        except (ValueError, TypeError):
            lines = 100

        try:
            result = HostInfoService.get_service_logs(host_id, service_name, lines)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @action(detail=False, methods=['post'], url_path='kill-process')
    def kill_process(self, request):
        """终止主机进程"""
        host_id = request.data.get('host_id')
        pid = request.data.get('pid')
        force = request.data.get('force', False)

        if not host_id or pid is None:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='host_id and pid are required')

        try:
            pid = int(pid)
        except (ValueError, TypeError):
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='pid must be an integer')

        try:
            result = HostInfoService.kill_process(host_id, pid, force)
            return SuccessResponse(result)
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)
