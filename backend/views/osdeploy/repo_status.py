"""RepoStatus 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import RepoStatus
from backend.serializers.osdeploy import (
    RepoStatusSerializer,
    RepoStatusListSerializer,
    RepoStatusCreateSerializer,
    RepoStatusUpdateSerializer,
)
from backend.schemas.osdeploy import RepoStatusResponse
from backend.common import SuccessResponse, ErrorResponse, ErrCode
from backend.common.viewsets import UnifiedModelViewSet


class RepoViewSet(UnifiedModelViewSet):
    """仓库状态视图集"""
    queryset = RepoStatus.objects.all().order_by('id')
    serializer_class = RepoStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'repo_type', 'is_default']
    search_fields = ['name']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return RepoStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return RepoStatusUpdateSerializer
        if self.action == 'list':
            return RepoStatusListSerializer
        return RepoStatusSerializer

    @extend_schema(
        summary="删除仓库",
        description="删除仓库前检查是否有关联的Kickstart模板",
        responses={
            200: OpenApiResponse(description="删除成功"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """删除仓库前检查是否有关联的 Kickstart"""
        repo = self.get_object()
        if repo.kickstartfilestatus_set.exists():
            return ErrorResponse(ErrCode.REPO_HAS_KICKSTART)
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="同步仓库",
        description="同步仓库内容",
        responses={
            200: OpenApiResponse(description="同步功能待实现"),
        }
    )
    @action(detail=True, methods=['post'], url_path='sync')
    def sync(self, request, pk=None):
        """同步仓库"""
        repo = self.get_object()
        # TODO: 调用 RepoService.sync_repo()
        return SuccessResponse(errmsg='仓库同步功能待实现')