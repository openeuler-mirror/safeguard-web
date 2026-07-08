"""KickStartFileStatus 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import KickStartFileStatus
from backend.serializers.osdeploy import (
    KickStartFileStatusSerializer,
    KickStartFileStatusListSerializer,
    KickStartFileStatusCreateSerializer,
    KickStartFileStatusUpdateSerializer,
)
from backend.schemas.osdeploy import KickStartFileStatusResponse
from backend.common import SuccessResponse, ErrorResponse, ErrCode
from backend.common.viewsets import UnifiedModelViewSet
from backend.services.osdeploy.kickstart_service import KickstartService


class KickStartViewSet(UnifiedModelViewSet):
    """Kickstart文件状态视图集"""
    queryset = KickStartFileStatus.objects.select_related('repo').all().order_by('id')
    serializer_class = KickStartFileStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'repo']
    search_fields = ['name']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return KickStartFileStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return KickStartFileStatusUpdateSerializer
        if self.action == 'list':
            return KickStartFileStatusListSerializer
        return KickStartFileStatusSerializer

    @extend_schema(
        summary="验证Kickstart模板",
        description="验证Kickstart模板语法是否正确",
        responses={200: OpenApiResponse(description="验证结果")}
    )
    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, pk=None):
        """验证Kickstart模板语法"""
        kickstart = self.get_object()
        result = KickstartService.validate_kickstart(kickstart.content)
        return SuccessResponse(result, errmsg='验证完成')

    @extend_schema(
        summary="预览Kickstart模板",
        description="预览生成的Kickstart文件内容，支持变量替换",
        responses={200: OpenApiResponse(description="模板预览")}
    )
    @action(detail=True, methods=['post'], url_path='preview')
    def preview(self, request, pk=None):
        """预览生成的Kickstart文件内容"""
        kickstart = self.get_object()
        vars = request.data.get('vars', {})
        content = KickstartService.render_template(kickstart.content, vars)
        return SuccessResponse({'content': content})

    @extend_schema(
        summary="基于模板生成Kickstart",
        description="基于现有模板进行变量替换生成Kickstart内容",
        responses={200: OpenApiResponse(description="生成的Kickstart内容")}
    )
    @action(detail=True, methods=['post'], url_path='generate')
    def generate(self, request, pk=None):
        """基于模板生成Kickstart"""
        kickstart = self.get_object()
        variables = request.data.get('variables', {})
        try:
            content = KickstartService.generate_kickstart(kickstart.id, variables)
        except ValueError as e:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg=str(e))
        return SuccessResponse({'content': content})

    @extend_schema(
        summary="自动全量生成Kickstart",
        description="根据主机信息自动全量生成Kickstart文件",
        responses={200: OpenApiResponse(description="自动生成的Kickstart内容")}
    )
    @action(detail=False, methods=['post'], url_path='auto_generate')
    def auto_generate(self, request):
        """自动全量生成Kickstart"""
        host_id = request.data.get('host_id')
        repo_id = request.data.get('repo_id')
        os_type = request.data.get('os_type', 'culinux')
        if not host_id or not repo_id:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='缺少 host_id 或 repo_id 参数')
        try:
            content = KickstartService.auto_generate_kickstart(host_id, repo_id, os_type)
        except ValueError as e:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg=str(e))
        return SuccessResponse({'content': content})

    @extend_schema(
        summary="生成系统配置文件",
        description="为所有 flag=True 的主机生成 system.conf 配置文件",
        responses={200: OpenApiResponse(description="生成结果")}
    )
    @action(detail=False, methods=['post'], url_path='system_conf')
    def system_conf(self, request):
        """生成 system.conf 配置文件"""
        output_path = request.data.get('output_path', '/var/www/html/pxe/conf/system.conf')
        from backend.common.exceptions import ServiceError
        try:
            result = KickstartService.generate_system_conf_file(output_path)
            return SuccessResponse(result, errmsg=result['message'])
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)

    @extend_schema(
        summary="生成网络配置文件",
        description="为所有 flag=True 的主机生成 network.conf 配置文件",
        responses={200: OpenApiResponse(description="生成结果")}
    )
    @action(detail=False, methods=['post'], url_path='network_conf')
    def network_conf(self, request):
        """生成 network.conf 配置文件"""
        output_path = request.data.get('output_path', '/var/www/html/pxe/conf/network.conf')
        from backend.common.exceptions import ServiceError
        try:
            result = KickstartService.generate_network_conf_file(output_path)
            return SuccessResponse(result, errmsg=result['message'])
        except ServiceError as e:
            return ErrorResponse(e.err_code, errmsg=e.err_msg)