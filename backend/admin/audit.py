"""Audit 模块 Admin 配置"""
from django.contrib import admin
from backend.models.audit import AuditLog, SystemLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """审计日志 Admin"""
    list_display = ['id', 'user', 'action', 'resource_type', 'status', 'created_at']
    list_filter = ['action', 'status', 'resource_type', 'created_at']
    search_fields = ['user__username', 'resource_name', 'action_details']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
    fieldsets = [
        ('基本信息', {'fields': ['user', 'action', 'status']}),
        ('资源信息', {'fields': ['resource_type', 'resource_id', 'resource_name']}),
        ('详细信息', {'fields': ['action_details', 'old_value', 'new_value']}),
        ('其他信息', {'fields': ['ip_address', 'user_agent', 'error_message']}),
    ]


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """系统日志 Admin"""
    list_display = ['id', 'host', 'source', 'level', 'timestamp']
    list_filter = ['host', 'source', 'level', 'timestamp']
    search_fields = ['message', 'host__hostname']
    readonly_fields = ['timestamp', 'collected_at']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    raw_id_fields = ['host']
