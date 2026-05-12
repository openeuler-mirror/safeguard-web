"""PXEServerStatus 序列化器"""
from rest_framework import serializers
from backend.models.osdeploy import PXEServerStatus


class PXEServerStatusSerializer(serializers.ModelSerializer):
    """PXE服务器状态序列化器"""

    class Meta:
        model = PXEServerStatus
        fields = [
            'id', 'server_ip', 'interface', 'dhcp_range_start',
            'dhcp_range_end', 'subnet', 'gateway', 'status',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PXEServerStatusListSerializer(serializers.ModelSerializer):
    """PXE服务器状态列表序列化器（简化字段）"""

    class Meta:
        model = PXEServerStatus
        fields = ['id', 'server_ip', 'interface', 'status']


class PXEServerStatusCreateSerializer(serializers.ModelSerializer):
    """PXE服务器创建序列化器"""

    class Meta:
        model = PXEServerStatus
        fields = [
            'server_ip', 'interface', 'dhcp_range_start',
            'dhcp_range_end', 'subnet', 'gateway', 'status', 'description'
        ]


class PXEServerStatusUpdateSerializer(serializers.ModelSerializer):
    """PXE服务器更新序列化器"""

    class Meta:
        model = PXEServerStatus
        fields = [
            'interface', 'dhcp_range_start', 'dhcp_range_end',
            'subnet', 'gateway', 'status', 'description'
        ]