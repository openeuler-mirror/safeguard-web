"""ISOFileStatus 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import ISOFileStatus


class ISOFileStatusSerializer(serializers.ModelSerializer):
    """ISO文件状态序列化器"""

    class Meta:
        model = ISOFileStatus
        fields = [
            'id', 'filename', 'size', 'md5sum', 'status',
            'file_path', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'md5sum', 'created_at', 'updated_at']


class ISOFileStatusListSerializer(serializers.ModelSerializer):
    """ISO文件状态列表序列化器（简化字段）"""

    class Meta:
        model = ISOFileStatus
        fields = ['id', 'filename', 'size', 'status']


class ISOFileStatusCreateSerializer(serializers.ModelSerializer):
    """ISO文件创建序列化器"""

    class Meta:
        model = ISOFileStatus
        fields = ['filename', 'size', 'md5sum', 'status', 'file_path', 'description']


class ISOFileStatusUpdateSerializer(serializers.ModelSerializer):
    """ISO文件更新序列化器"""

    class Meta:
        model = ISOFileStatus
        fields = ['status', 'description']