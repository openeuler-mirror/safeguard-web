"""KickStartFileStatus 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import KickStartFileStatus


class KickStartFileStatusSerializer(serializers.ModelSerializer):
    """Kickstart文件状态序列化器"""
    repo_name = serializers.CharField(source='repo.name', read_only=True, allow_null=True)

    class Meta:
        model = KickStartFileStatus
        fields = [
            'id', 'name', 'content', 'repo', 'repo_name',
            'kernel_options', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class KickStartFileStatusListSerializer(serializers.ModelSerializer):
    """Kickstart文件状态列表序列化器（简化字段）"""
    repo_name = serializers.CharField(source='repo.name', read_only=True, allow_null=True)

    class Meta:
        model = KickStartFileStatus
        fields = ['id', 'name', 'repo', 'repo_name']


class KickStartFileStatusCreateSerializer(serializers.ModelSerializer):
    """Kickstart文件创建序列化器"""

    class Meta:
        model = KickStartFileStatus
        fields = ['name', 'content', 'repo', 'kernel_options', 'description']


class KickStartFileStatusUpdateSerializer(serializers.ModelSerializer):
    """Kickstart文件更新序列化器"""

    class Meta:
        model = KickStartFileStatus
        fields = ['name', 'content', 'repo', 'kernel_options', 'description']