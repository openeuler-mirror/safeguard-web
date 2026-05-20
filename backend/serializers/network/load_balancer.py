"""LoadBalancer 序列化器"""
from rest_framework import serializers
from backend.models.network import LoadBalancer


class LoadBalancerSerializer(serializers.ModelSerializer):
    """负载均衡器序列化器"""

    class Meta:
        model = LoadBalancer
        fields = [
            'id', 'name', 'vip_address', 'port', 'algorithm',
            'status', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoadBalancerListSerializer(serializers.ModelSerializer):
    """负载均衡器列表序列化器（简化字段）"""

    class Meta:
        model = LoadBalancer
        fields = ['id', 'name', 'vip_address', 'port', 'algorithm', 'status']


class LoadBalancerCreateSerializer(serializers.ModelSerializer):
    """负载均衡器创建序列化器"""

    class Meta:
        model = LoadBalancer
        fields = ['name', 'vip_address', 'port', 'algorithm', 'status', 'description']


class LoadBalancerUpdateSerializer(serializers.ModelSerializer):
    """负载均衡器更新序列化器"""

    class Meta:
        model = LoadBalancer
        fields = ['name', 'vip_address', 'port', 'algorithm', 'status', 'description']