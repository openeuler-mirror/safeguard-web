"""WhiteList 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import WhiteList


class WhiteListSerializer(serializers.ModelSerializer):
    """MAC地址白名单序列化器"""

    class Meta:
        model = WhiteList
        fields = [
            'id', 'mac_address', 'hostname', 'ip_address',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WhiteListListSerializer(serializers.ModelSerializer):
    """MAC地址白名单列表序列化器（简化字段）"""

    class Meta:
        model = WhiteList
        fields = ['id', 'mac_address', 'hostname', 'ip_address', 'is_active']


class WhiteListCreateSerializer(serializers.ModelSerializer):
    """MAC地址白名单创建序列化器"""

    class Meta:
        model = WhiteList
        fields = ['mac_address', 'hostname', 'ip_address', 'description', 'is_active']


class WhiteListUpdateSerializer(serializers.ModelSerializer):
    """MAC地址白名单更新序列化器"""

    class Meta:
        model = WhiteList
        fields = ['hostname', 'ip_address', 'description', 'is_active']