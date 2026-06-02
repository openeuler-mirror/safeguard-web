"""OSmigrate 迁移视图集"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.models.osmigrate.migrate_job import MigrateJob
from backend.serializers.osmigrate.migrate import (
    MigrateJobSerializer,
    MigrateJobListSerializer,
    MigrateInitSerializer,
    MigrateSerializer,
    MigrateBackSerializer,
)
from backend.services.osmigrate.x2cu_service import X2cuService
from backend.common import SuccessResponse, ErrorResponse


class MigrateViewSet(viewsets.ModelViewSet):
    """系统迁移视图集"""

    queryset = MigrateJob.objects.all().order_by("-id")
    serializer_class = MigrateJobSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["job_type", "migrate_type", "status", "target_host"]
    search_fields = ["job_id", "target_host"]
    ordering_fields = ["created_at", "id"]

    def get_serializer_class(self):
        if self.action == "list":
            return MigrateJobListSerializer
        return MigrateJobSerializer

    @action(["post"], False)
    def init(self, request):
        """迁移初始化"""
        serializer = MigrateInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        job_id = X2cuService.start_migrate_init(
            host=data["host"],
            port=data.get("port", "22"),
            username=data["username"],
            password=data["password"],
            hosts=data.get("hosts", []),
            migrate_type=data.get("type", [""])[0] if data.get("type") else "",
            redis_passwd=data.get("redispasswd", ""),
        )
        return SuccessResponse({"job_id": job_id, "message": "create migrate init job success"})

    @action(["post"], False)
    def migrate(self, request):
        """执行迁移"""
        serializer = MigrateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        job_id = X2cuService.start_migrate(
            job_name=data.get("jobname", ""),
            host=data["host"],
            port=data.get("port", "22"),
            username=data["username"],
            password=data["password"],
            hosts=data.get("hosts", []),
            migrate_type=data.get("type", [""])[0] if data.get("type") else "",
        )
        return SuccessResponse({"job_id": job_id, "message": "create migrate job success"})

    @action(["post"], False)
    def back(self, request):
        """迁移回滚"""
        serializer = MigrateBackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        job_id = X2cuService.start_migrate_back(
            job_name=data.get("jobname", ""),
            host=data["host"],
            port=data.get("port", "22"),
            username=data["username"],
            password=data["password"],
        )
        return SuccessResponse({"job_id": job_id, "message": "create migrate back job success"})

    @action(["get"], True)
    def status(self, request, pk=None):
        """获取迁移任务状态"""
        job = self.get_object()
        result = X2cuService.get_migrate_status(job.job_id)
        if result:
            return SuccessResponse(result)
        return ErrorResponse("任务不存在")
