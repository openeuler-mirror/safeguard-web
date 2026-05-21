"""JobStatus 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import JobStatus
from backend.serializers.osdeploy import JobStatusSerializer, JobStatusListSerializer
from backend.schemas.osdeploy import JobStatusResponse
from backend.services.osdeploy import DeployService
from backend.common import SuccessResponse, ErrorResponse, ErrCode
from backend.common.viewsets import UnifiedModelViewSet


class JobViewSet(UnifiedModelViewSet):
    """任务状态视图集（只读）"""
    queryset = JobStatus.objects.all().order_by('-created_at')
    serializer_class = JobStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['job_type', 'status']
    search_fields = ['job_id', 'target']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'list':
            return JobStatusListSerializer
        return JobStatusSerializer

    @extend_schema(
        summary="查询任务状态",
        description="根据job_id查询任务状态",
        responses={
            200: OpenApiResponse(response=JobStatusResponse, description="任务详情"),
        }
    )
    @action(detail=False, methods=['get'], url_path='query')
    def query(self, request):
        """
        根据job_id查询任务状态
        GET /api/jobs/query/?job_id=xxx
        """
        job_id = request.query_params.get('job_id')
        if not job_id:
            return ErrorResponse(ErrCode.PARAM_ERROR, errmsg='job_id参数必填')

        job = DeployService.query_job_status(job_id)
        if not job:
            return ErrorResponse(ErrCode.NOT_FOUND, errmsg='任务不存在')

        serializer = JobStatusSerializer(job)
        return SuccessResponse(serializer.data)