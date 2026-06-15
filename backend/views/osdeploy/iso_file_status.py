"""ISOFileStatus 视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from backend.models.osdeploy import ISOFileStatus
from backend.serializers.osdeploy import (
    ISOFileStatusSerializer,
    ISOFileStatusListSerializer,
    ISOFileStatusCreateSerializer,
    ISOFileStatusUpdateSerializer,
)
from backend.common import SuccessResponse, ErrorResponse, ErrCode, UnifiedModelViewSet


class ISOFileStatusViewSet(UnifiedModelViewSet):
    """ISO文件状态视图集"""
    queryset = ISOFileStatus.objects.all().order_by('id')
    serializer_class = ISOFileStatusSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['filename', 'status']
    search_fields = ['filename']
    ordering_fields = ['created_at', 'id']

    def get_serializer_class(self):
        if self.action == 'create':
            return ISOFileStatusCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ISOFileStatusUpdateSerializer
        if self.action == 'list':
            return ISOFileStatusListSerializer
        return ISOFileStatusSerializer

    @extend_schema(
        summary="上传ISO文件",
        description="接收ISO文件上传并创建记录",
        responses={200: OpenApiResponse(description="上传结果")}
    )
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """上传ISO文件"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return ErrorResponse(ErrCode.PARAMETER_MISSING, errmsg='请上传ISO文件')

        iso = ISOFileStatus.objects.create(
            filename=file_obj.name,
            size=file_obj.size,
            status='available',
            file_path='',
        )
        serializer = ISOFileStatusSerializer(iso)
        return SuccessResponse(serializer.data, errmsg='上传成功')
