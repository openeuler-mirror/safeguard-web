from rest_framework import serializers
from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)


class SafeguardPolicyTemplateSerializer(serializers.ModelSerializer):
    """策略模板序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)

    class Meta:
        model = SafeguardPolicyTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'is_builtin',
            'config', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SafeguardPolicyTemplateCreateSerializer(serializers.ModelSerializer):
    """策略模板创建序列化器"""
    class Meta:
        model = SafeguardPolicyTemplate
        fields = ['name', 'description', 'template_type', 'config']


class SafeguardPolicyTemplateUpdateSerializer(serializers.ModelSerializer):
    """策略模板更新序列化器"""
    class Meta:
        model = SafeguardPolicyTemplate
        fields = ['name', 'description', 'template_type', 'config']


class HostSafeguardPolicySerializer(serializers.ModelSerializer):
    """主机策略序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)

    class Meta:
        model = HostSafeguardPolicy
        fields = [
            'id', 'host', 'host_name', 'template', 'template_name',
            'config', 'config_version', 'applied_at', 'status',
            'last_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'config_version', 'created_at', 'updated_at']


class PolicyApplyTaskSerializer(serializers.ModelSerializer):
    """策略下发任务序列化器"""
    host_name = serializers.CharField(source='host.hostname', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)

    class Meta:
        model = PolicyApplyTask
        fields = [
            'id', 'host', 'host_name', 'policy', 'task_type',
            'status', 'message', 'started_at', 'finished_at',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
