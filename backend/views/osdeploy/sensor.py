"""Sensor 部署管理视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.services.osdeploy.sensor_service import SensorService
from backend.schemas.osdeploy.sensor import (
    SensorDeploymentConfig,
    SensorOperateRequest,
    SensorConfigUpdateRequest,
)
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class SensorViewSet(viewsets.ViewSet):
    """Sensor 部署管理视图集"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='install')
    def install(self, request):
        """安装 sensor"""
        try:
            config = SensorDeploymentConfig.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = SensorService.install_sensor(config.model_dump())
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result['message'])
        return SuccessResponse({
            'job_id': result['job_id'],
            'status': result['status'],
        }, errmsg=result['message'])

    @action(detail=False, methods=['post'], url_path='update-config')
    def update_config(self, request):
        """更新 sensor 配置并重启服务"""
        serial_number = request.data.get('serial_number')
        if not serial_number:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='serial_number is required')

        host_info = request.data.get('host_info')
        if not host_info:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='host_info is required')

        try:
            schema = SensorConfigUpdateRequest.model_validate(
                {'config': request.data.get('config', {})}
            )
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = SensorService.update_config(
            serial_number,
            schema.config,
            host_info,
        )
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result['message'])
        return SuccessResponse({
            'config': result['config'],
        }, errmsg=result['message'])

    @action(detail=False, methods=['post'], url_path='operate')
    def operate(self, request):
        """操作 sensor 服务 (start/stop/restart/delete)"""
        try:
            req = SensorOperateRequest.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = SensorService.operate_sensor(
            {
                'host': req.host,
                'username': req.username,
                'password': req.password,
                'port': req.port,
            },
            req.operate,
        )
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.OPERATION_FAILED, errmsg=result['message'])
        return SuccessResponse({
            'output': result.get('output', ''),
        }, errmsg=result['message'])
