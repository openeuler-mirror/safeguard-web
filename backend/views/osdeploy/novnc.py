"""noVNC 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.schemas.osdeploy.novnc import NoVNCClient
from backend.services.osdeploy.novnc_service import NoVNCService
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class NoVNCViewSet(viewsets.ViewSet):
    """noVNC 管理视图集"""
    permission_classes = [IsAuthenticated]

    @action(['post'], False, url_path='install')
    def install(self, request):
        """安装并启动 noVNC"""
        try:
            config = NoVNCClient.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = NoVNCService.install_novnc(config.model_dump())
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=result['message'])
        return SuccessResponse(errmsg=result['message'])

    @action(['post'], False, url_path='close')
    def close(self, request):
        """关闭 noVNC"""
        try:
            config = NoVNCClient.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = NoVNCService.close_novnc(config.model_dump())
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=result['message'])
        return SuccessResponse(errmsg=result['message'])