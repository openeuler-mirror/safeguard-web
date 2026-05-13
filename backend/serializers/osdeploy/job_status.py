"""JobStatus 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import JobStatus


class JobStatusSerializer(serializers.ModelSerializer):
    """任务状态序列化器"""

    class Meta:
        model = JobStatus
        fields = [
            'id', 'job_id', 'job_type', 'target', 'status',
            'progress', 'result', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'job_id', 'created_at', 'updated_at']


class JobStatusListSerializer(serializers.ModelSerializer):
    """任务状态列表序列化器（简化字段）"""

    class Meta:
        model = JobStatus
        fields = [
            'id', 'job_id', 'job_type', 'target', 'status',
            'progress', 'created_at'
        ]