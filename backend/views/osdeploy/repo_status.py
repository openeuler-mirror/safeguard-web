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
from backend.services.osdeploy.repo_service import RepoService
from backend.services.task import TaskService
from backend.utils.ssh import SSHClient


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
        responses={200: OpenApiResponse(description="同步结果")}
    )
    @action(detail=True, methods=['post'], url_path='sync')
    def sync(self, request, pk=None):
        """同步仓库"""
        repo = self.get_object()
        result = RepoService.sync_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="启用仓库",
        description="启用指定仓库",
        responses={200: OpenApiResponse(description="启用结果")}
    )
    @action(detail=True, methods=['post'], url_path='enable')
    def enable(self, request, pk=None):
        """启用仓库"""
        repo = self.get_object()
        result = RepoService.enable_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="禁用仓库",
        description="禁用指定仓库",
        responses={200: OpenApiResponse(description="禁用结果")}
    )
    @action(detail=True, methods=['post'], url_path='disable')
    def disable(self, request, pk=None):
        """禁用仓库"""
        repo = self.get_object()
        result = RepoService.disable_repo(repo.id)
        return SuccessResponse(result)

    @extend_schema(
        summary="检查仓库",
        description="检查仓库可用性",
        responses={200: OpenApiResponse(description="检查结果")}
    )
    @action(detail=True, methods=['get'], url_path='check')
    def check(self, request, pk=None):
        """检查仓库"""
        repo = self.get_object()
        result = RepoService.check_repo(repo.id)
        return SuccessResponse(result)