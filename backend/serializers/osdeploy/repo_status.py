"""RepoStatus 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import RepoStatus


class RepoStatusSerializer(serializers.ModelSerializer):
    """仓库状态序列化器"""

    class Meta:
        model = RepoStatus
        fields = [
            'id', 'name', 'repo_type', 'base_url',
            'is_default', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RepoStatusListSerializer(serializers.ModelSerializer):
    """仓库状态列表序列化器（简化字段）"""

    class Meta:
        model = RepoStatus
        fields = ['id', 'name', 'repo_type', 'is_default']


class RepoStatusCreateSerializer(serializers.ModelSerializer):
    """仓库创建序列化器"""

    class Meta:
        model = RepoStatus
        fields = ['name', 'repo_type', 'base_url', 'is_default', 'description']


class RepoStatusUpdateSerializer(serializers.ModelSerializer):
    """仓库更新序列化器"""

    class Meta:
        model = RepoStatus
        fields = ['name', 'repo_type', 'base_url', 'is_default', 'description']