"""Task 任务视图集"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.models.task import Task
from backend.serializers.task import (
    TaskSerializer,
    TaskListSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskQuerySerializer,
)
from backend.common.viewsets import UnifiedModelViewSet
from backend.services.task import TaskService
from backend.common import SuccessResponse


class TaskViewSet(UnifiedModelViewSet):
    """任务管理视图集"""

    queryset = Task.objects.all().order_by("-id")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["job_type", "status", "target"]
    search_fields = ["job_id", "target"]
    ordering_fields = ["created_at", "id"]

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        if self.action in ("update", "partial_update"):
            return TaskUpdateSerializer
        if self.action == "list":
            return TaskListSerializer
        return TaskSerializer

    def _serialize_task_result(self, result):
        """序列化任务查询结果中的模型对象"""
        result = dict(result)
        result["results"] = TaskListSerializer(result["results"], many=True).data
        return result

    @action(["post"], False)
    def query(self, request):
        """按条件查询任务"""
        serializer = TaskQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        condition = {
            k: v
            for k, v in serializer.validated_data.items()
            if v
        }
        # 安全解析分页参数
        try:
            page = int(request.query_params.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        # 确保 page >= 1
        if page < 1:
            page = 1

        try:
            page_size = int(request.query_params.get("page_size", 10))
        except (ValueError, TypeError):
            page_size = 10
        # 确保 page_size 在合理范围内 (1-1000)
        if page_size < 1:
            page_size = 10
        if page_size > 1000:
            page_size = 1000
        result = TaskService.query_by_condition(
            condition=condition, page=page, page_size=page_size
        )
        return SuccessResponse(self._serialize_task_result(result))

    @action(["post"], False)
    def page(self, request):
        """分页查询任务（支持复杂过滤）"""
        serializer = TaskQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        condition = {
            k: v
            for k, v in serializer.validated_data.items()
            if v
        }
        # 安全解析分页参数
        try:
            page = int(request.query_params.get("page", 1))
        except (ValueError, TypeError):
            page = 1
        # 确保 page >= 1
        if page < 1:
            page = 1

        try:
            page_size = int(request.query_params.get("page_size", 10))
        except (ValueError, TypeError):
            page_size = 10
        # 确保 page_size 在合理范围内 (1-1000)
        if page_size < 1:
            page_size = 10
        if page_size > 1000:
            page_size = 1000
        result = TaskService.query_by_condition(
            condition=condition, page=page, page_size=page_size
        )
        return SuccessResponse(self._serialize_task_result(result))