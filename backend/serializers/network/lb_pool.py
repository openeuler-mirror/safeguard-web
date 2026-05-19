"""LBPool 序列化器"""
from rest_framework import serializers
from backend.models.network import LBPool


class LBPoolSerializer(serializers.ModelSerializer):
    """后端池序列化器"""
    loadbalancer_name = serializers.CharField(source='loadbalancer.name', read_only=True)

    class Meta:
        model = LBPool
        fields = [
            'id', 'name', 'loadbalancer', 'loadbalancer_name',
            'protocol', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LBPoolListSerializer(serializers.ModelSerializer):
    """后端池列表序列化器（简化字段）"""
    loadbalancer_name = serializers.CharField(source='loadbalancer.name', read_only=True)

    class Meta:
        model = LBPool
        fields = ['id', 'name', 'loadbalancer', 'loadbalancer_name', 'protocol']


class LBPoolCreateSerializer(serializers.ModelSerializer):
    """后端池创建序列化器"""

    class Meta:
        model = LBPool
        fields = ['name', 'loadbalancer', 'protocol', 'description']


class LBPoolUpdateSerializer(serializers.ModelSerializer):
    """后端池更新序列化器"""

    class Meta:
        model = LBPool
        fields = ['name', 'protocol', 'description']