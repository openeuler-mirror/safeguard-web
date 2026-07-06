from rest_framework import serializers
from backend.models.safeguard.monitor import HostMonitorData


class HostMonitorDataSerializer(serializers.ModelSerializer):
    """主机监控数据序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = HostMonitorData
        fields = [
            'id', 'host', 'host_name', 'timestamp',
            'cpu_usage', 'load_1m', 'load_5m', 'load_15m',
            'memory_total', 'memory_used', 'memory_usage',
            'network_in', 'network_out',
            'disk_read', 'disk_write',
        ]
        read_only_fields = ['id', 'timestamp']
