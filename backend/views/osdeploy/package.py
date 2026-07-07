"""软件包配置视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from pydantic import ValidationError

from backend.schemas.osdeploy.package import SpecParams
from backend.services.osdeploy.package_service import PackageService
from backend.common import SuccessResponse, ErrorResponse, ErrCode, ServiceError


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

        try:
            result = PackageService.generate_spec(params.model_dump())
            return SuccessResponse({
                "path": result["path"],
                "content": result["content"]
            }, errmsg=result.get("message"))
        except ServiceError as e:
            return ErrorResponse(ErrCode.INTERNAL_ERROR, errmsg=e.err_msg)
