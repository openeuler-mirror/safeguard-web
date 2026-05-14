"""OS部署相关 Admin 配置"""
from django.contrib import admin
from backend.models.osdeploy import (
    JobStatus,
    RepoStatus,
    PXEServerStatus,
    KickStartFileStatus,
    ISOFileStatus,
    WhiteList,
    OutIpSN,
)


@admin.register(JobStatus)
class JobStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_id', 'job_type', 'target', 'status', 'progress', 'created_at']
    list_filter = ['status', 'job_type', 'created_at']
    search_fields = ['job_id', 'target']
    ordering = ['-created_at']
    list_per_page = 20
    readonly_fields = ['job_id', 'created_at', 'updated_at']


@admin.register(RepoStatus)
class RepoStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'repo_type', 'base_url', 'is_default', 'created_at']
    list_filter = ['repo_type', 'is_default', 'created_at']
    search_fields = ['name', 'base_url']
    ordering = ['id']
    list_per_page = 20


@admin.register(PXEServerStatus)
class PXEServerStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'server_ip', 'interface', 'dhcp_range_start', 'dhcp_range_end', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['server_ip']
    ordering = ['id']
    list_per_page = 20


@admin.register(KickStartFileStatus)
class KickStartFileStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'repo', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['id']
    list_per_page = 20


@admin.register(ISOFileStatus)
class ISOFileStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'size', 'md5sum', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['filename']
    ordering = ['id']
    list_per_page = 20


@admin.register(WhiteList)
class WhiteListAdmin(admin.ModelAdmin):
    list_display = ['id', 'mac_address', 'hostname', 'ip_address', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['mac_address', 'hostname', 'ip_address']
    ordering = ['id']
    list_per_page = 20


@admin.register(OutIpSN)
class OutIpSNAdmin(admin.ModelAdmin):
    list_display = ['id', 'mac_address', 'sn', 'created_at']
    list_filter = ['created_at']
    search_fields = ['mac_address', 'sn']
    ordering = ['id']
    list_per_page = 20