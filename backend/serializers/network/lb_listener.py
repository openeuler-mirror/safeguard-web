"""LBListener 序列化器"""
from rest_framework import serializers
from backend.models.network import LBListener


class LBListenerSerializer(serializers.ModelSerializer):
    """监听器序列化器"""
    loadbalancer_name = serializers.CharField(source='loadbalancer.name', read_only=True)

    class Meta:
        model = LBListener
        fields = [
            'id', 'loadbalancer', 'loadbalancer_name', 'protocol',
            'port', 'name', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LBListenerListSerializer(serializers.ModelSerializer):
    """监听器列表序列化器（简化字段）"""
    loadbalancer_name = serializers.CharField(source='loadbalancer.name', read_only=True)

    class Meta:
        model = LBListener
        fields = ['id', 'loadbalancer', 'loadbalancer_name', 'protocol', 'port', 'name']


class LBListenerCreateSerializer(serializers.ModelSerializer):
    """监听器创建序列化器"""

    class Meta:
        model = LBListener
        fields = ['loadbalancer', 'protocol', 'port', 'name', 'description']


class LBListenerUpdateSerializer(serializers.ModelSerializer):
    """监听器更新序列化器"""

    class Meta:
        model = LBListener
        fields = ['protocol', 'port', 'name', 'description']