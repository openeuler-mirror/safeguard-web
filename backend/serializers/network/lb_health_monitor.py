"""LBHealthMonitor 序列化器"""
from rest_framework import serializers
from backend.models.network import LBHealthMonitor


class LBHealthMonitorSerializer(serializers.ModelSerializer):
    """健康检查序列化器"""
    pool_name = serializers.CharField(source='pool.name', read_only=True)

    class Meta:
        model = LBHealthMonitor
        fields = [
            'id', 'pool', 'pool_name', 'monitor_type',
            'interval', 'timeout', 'retry', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LBHealthMonitorListSerializer(serializers.ModelSerializer):
    """健康检查列表序列化器（简化字段）"""
    pool_name = serializers.CharField(source='pool.name', read_only=True)

    class Meta:
        model = LBHealthMonitor
        fields = ['id', 'pool', 'pool_name', 'monitor_type', 'interval', 'timeout', 'retry']


class LBHealthMonitorCreateSerializer(serializers.ModelSerializer):
    """健康检查创建序列化器"""

    class Meta:
        model = LBHealthMonitor
        fields = ['pool', 'monitor_type', 'interval', 'timeout', 'retry', 'description']


class LBHealthMonitorUpdateSerializer(serializers.ModelSerializer):
    """健康检查更新序列化器"""

    class Meta:
        model = LBHealthMonitor
        fields = ['monitor_type', 'interval', 'timeout', 'retry', 'description']