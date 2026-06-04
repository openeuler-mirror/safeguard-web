"""软件包配置视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.schemas.osdeploy.package import SpecParams
from backend.services.osdeploy.package_service import PackageService
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class PackageViewSet(viewsets.ViewSet):
    """RPM 包配置视图集"""
    permission_classes = [IsAuthenticated]

    @action(['post'], False, url_path='config')
    def config(self, request):
        """生成 RPM spec 配置文件"""
        try:
            params = SpecParams.model_validate(request.data)
        except ValidationError as e:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg=str(e.errors()))

        result = PackageService.generate_spec(params.model_dump())
        if result['status'] == 'failed':
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=result['message'])
        return SuccessResponse({
            'path': result['path'],
            'content': result['content'],
        }, errmsg=result['message'])