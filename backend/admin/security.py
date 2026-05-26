"""Security 模块 Admin 配置"""
from django.contrib import admin
from backend.models.security import SafeguardDeploy


@admin.register(SafeguardDeploy)
class SafeguardDeployAdmin(admin.ModelAdmin):
    """Safeguard 部署 Admin"""
    list_display = ['id', 'name', 'safeguard_type', 'arch', 'host', 'status', 'created_at']
    list_filter = ['status', 'safeguard_type', 'arch']
    search_fields = ['name', 'host']
    readonly_fields = ['status', 'result', 'error_message', 'created_at', 'updated_at']
    ordering = ['-created_at']