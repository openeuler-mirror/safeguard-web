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
from backend.common import SuccessResponse
from backend.common.viewsets import UnifiedModelViewSet


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
        responses={200: OpenApiResponse(description="验证功能待实现")}
    )
    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, pk=None):
        """验证Kickstart模板语法"""
        kickstart = self.get_object()
        # TODO: 调用 DeployService.validate_kickstart()
        return SuccessResponse(errmsg='Kickstart模板验证功能待实现')

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
        # TODO: 调用 DeployService.generate_kickstart()
        content = kickstart.content
        # 简单的变量替换预览
        for key, value in vars.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return SuccessResponse({'content': content})