"""noVNC 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.schemas.osdeploy.novnc import NoVNCClient
from backend.services.osdeploy.novnc_service import NoVNCService
from backend.common import SuccessResponse, ErrorResponse, ErrCode, ServiceError


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

        try:
            result = NoVNCService.install_novnc(config.model_dump())
            return SuccessResponse(errmsg=result.get("message"))
        except ServiceError as e:
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=e.err_msg)

    @action(['post'], False, url_path='close')
    def close(self, request):
        """关闭 noVNC"""
        try:
            config = NoVNCClient.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        try:
            result = NoVNCService.close_novnc(config.model_dump())
            return SuccessResponse(errmsg=result.get("message"))
        except ServiceError as e:
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=e.err_msg)
