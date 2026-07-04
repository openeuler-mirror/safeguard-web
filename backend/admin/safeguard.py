"""Safeguard 模块 Admin 配置"""
from django.contrib import admin
from backend.models.safeguard import (
    HostMonitorData,
    FileMonitorRule,
    FileMonitorEvent,
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)


@admin.register(HostMonitorData)
class HostMonitorDataAdmin(admin.ModelAdmin):
    """主机监控数据 Admin"""
    list_display = ['id', 'host', 'timestamp', 'cpu_usage', 'memory_usage', 'load_1m']
    list_filter = ['host', 'timestamp']
    search_fields = ['host__hostname']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(FileMonitorRule)
class FileMonitorRuleAdmin(admin.ModelAdmin):
    """文件监控规则 Admin"""
    list_display = ['id', 'host', 'path', 'monitor_type', 'enabled', 'created_at']
    list_filter = ['host', 'monitor_type', 'enabled']
    search_fields = ['path', 'host__hostname']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(FileMonitorEvent)
class FileMonitorEventAdmin(admin.ModelAdmin):
    """文件监控事件 Admin"""
    list_display = ['id', 'host', 'event_type', 'path', 'timestamp']
    list_filter = ['host', 'event_type', 'timestamp']
    search_fields = ['path', 'host__hostname']
    readonly_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SafeguardPolicyTemplate)
class SafeguardPolicyTemplateAdmin(admin.ModelAdmin):
    """策略模板 Admin"""
    list_display = ['id', 'name', 'template_type', 'is_builtin', 'created_at']
    list_filter = ['template_type', 'is_builtin']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(HostSafeguardPolicy)
class HostSafeguardPolicyAdmin(admin.ModelAdmin):
    """主机策略 Admin"""
    list_display = ['id', 'host', 'template', 'status', 'applied_at']
    list_filter = ['status', 'template']
    search_fields = ['host__hostname']
    readonly_fields = ['applied_at', 'last_sync', 'created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['host', 'template']


@admin.register(PolicyApplyTask)
class PolicyApplyTaskAdmin(admin.ModelAdmin):
    """策略下发任务 Admin"""
    list_display = ['id', 'host', 'policy', 'task_type', 'status', 'started_at']
    list_filter = ['task_type', 'status']
    search_fields = ['host__hostname']
    readonly_fields = ['started_at', 'finished_at', 'created_at']
    ordering = ['-created_at']
    raw_id_fields = ['host', 'policy']
