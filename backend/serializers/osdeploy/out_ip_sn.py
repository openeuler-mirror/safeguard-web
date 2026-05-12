"""OutIpSN 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import OutIpSN


class OutIpSNSerializer(serializers.ModelSerializer):
    """出口IP序列号序列化器"""

    class Meta:
        model = OutIpSN
        fields = [
            'id', 'mac_address', 'sn', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OutIpSNListSerializer(serializers.ModelSerializer):
    """出口IP序列号列表序列化器（简化字段）"""

    class Meta:
        model = OutIpSN
        fields = ['id', 'mac_address', 'sn']


class OutIpSNCreateSerializer(serializers.ModelSerializer):
    """出口IP序列号创建序列化器"""

    class Meta:
        model = OutIpSN
        fields = ['mac_address', 'sn', 'description']


class OutIpSNUpdateSerializer(serializers.ModelSerializer):
    """出口IP序列号更新序列化器"""

    class Meta:
        model = OutIpSN
        fields = ['sn', 'description']