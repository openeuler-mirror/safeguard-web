from rest_framework import serializers
from backend.models.audit.audit_log import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'resource_type',
            'resource_id', 'resource_name', 'action_details',
            'old_value', 'new_value', 'ip_address', 'user_agent',
            'status', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
