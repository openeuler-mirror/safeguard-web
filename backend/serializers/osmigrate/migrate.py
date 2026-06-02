"""OSmigrate 序列化器"""
from rest_framework import serializers
from backend.models.osmigrate.migrate_job import MigrateJob


class MigrateJobSerializer(serializers.ModelSerializer):
    """迁移任务标准序列化器"""

    class Meta:
        model = MigrateJob
        fields = [
            "id",
            "job_id",
            "job_type",
            "migrate_type",
            "target_host",
            "hosts_json",
            "status",
            "progress",
            "result",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MigrateJobListSerializer(serializers.ModelSerializer):
    """迁移任务列表序列化器"""

    class Meta:
        model = MigrateJob
        fields = [
            "id",
            "job_id",
            "job_type",
            "migrate_type",
            "target_host",
            "status",
            "progress",
            "created_at",
        ]


class HostInfoSerializer(serializers.Serializer):
    """主机信息序列化器"""
    host = serializers.CharField(required=True)
    port = serializers.CharField(required=False, default="22")
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class MigrateInitSerializer(serializers.Serializer):
    """迁移初始化请求序列化器"""
    host = serializers.CharField(required=True)
    port = serializers.CharField(required=False, default="22")
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    type = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    hosts = HostInfoSerializer(many=True, required=False)
    redispasswd = serializers.CharField(required=False, allow_blank=True)


class MigrateSerializer(serializers.Serializer):
    """迁移执行请求序列化器"""
    host = serializers.CharField(required=True)
    port = serializers.CharField(required=False, default="22")
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    jobname = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    hosts = HostInfoSerializer(many=True, required=False)


class MigrateBackSerializer(serializers.Serializer):
    """迁移回滚请求序列化器"""
    host = serializers.CharField(required=True)
    port = serializers.CharField(required=False, default="22")
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    jobname = serializers.CharField(required=False, allow_blank=True)
