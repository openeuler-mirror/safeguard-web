"""Task 序列化器"""
from rest_framework import serializers
from backend.models.task import Task


class TaskSerializer(serializers.ModelSerializer):
    """Task 标准序列化器"""

    class Meta:
        model = Task
        fields = [
            "id",
            "job_id",
            "job_type",
            "target",
            "status",
            "progress",
            "result",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskListSerializer(serializers.ModelSerializer):
    """Task 列表序列化器（精简字段）"""

    class Meta:
        model = Task
        fields = [
            "id",
            "job_id",
            "job_type",
            "target",
            "status",
            "progress",
            "created_at",
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Task 创建序列化器"""

    class Meta:
        model = Task
        fields = [
            "job_id",
            "job_type",
            "target",
            "status",
            "progress",
            "result",
            "error_message",
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Task 更新序列化器"""

    class Meta:
        model = Task
        fields = [
            "status",
            "progress",
            "result",
            "error_message",
        ]


class TaskQuerySerializer(serializers.Serializer):
    """Task 条件查询序列化器"""

    job_type = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    target = serializers.CharField(required=False, allow_blank=True)