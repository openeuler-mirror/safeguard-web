from rest_framework import serializers
from backend.models.safeguard.file_monitor import (
    FileMonitorRule,
    FileMonitorEvent,
)


class FileMonitorRuleSerializer(serializers.ModelSerializer):
    """文件监控规则序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = FileMonitorRule
        fields = [
            'id', 'host', 'host_name', 'path', 'monitor_type',
            'watch_create', 'watch_modify', 'watch_delete',
            'watch_access', 'watch_perm', 'recursive',
            'includes', 'excludes', 'enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FileMonitorRuleCreateSerializer(serializers.ModelSerializer):
    """文件监控规则创建序列化器"""
    class Meta:
        model = FileMonitorRule
        fields = [
            'host', 'path', 'monitor_type',
            'watch_create', 'watch_modify', 'watch_delete',
            'watch_access', 'watch_perm', 'recursive',
            'includes', 'excludes', 'enabled'
        ]


class FileMonitorRuleUpdateSerializer(serializers.ModelSerializer):
    """文件监控规则更新序列化器"""
    class Meta:
        model = FileMonitorRule
        fields = [
            'path', 'monitor_type',
            'watch_create', 'watch_modify', 'watch_delete',
            'watch_access', 'watch_perm', 'recursive',
            'includes', 'excludes', 'enabled'
        ]


class FileMonitorEventSerializer(serializers.ModelSerializer):
    """文件监控事件序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = FileMonitorEvent
        fields = [
            'id', 'host', 'host_name', 'rule', 'event_type',
            'path', 'process_name', 'process_id', 'user',
            'timestamp', 'details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
