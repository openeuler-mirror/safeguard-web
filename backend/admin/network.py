"""Network 相关 Admin 配置"""
from django.contrib import admin
from backend.models.network import (
    LoadBalancer,
    LBListener,
    LBPool,
    LBMember,
    LBHealthMonitor,
)


@admin.register(LoadBalancer)
class LoadBalancerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'vip_address', 'port', 'algorithm', 'status', 'created_at']
    list_filter = ['status', 'algorithm', 'created_at']
    search_fields = ['name', 'vip_address']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(LBListener)
class LBListenerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'loadbalancer', 'protocol', 'port', 'created_at']
    list_filter = ['protocol', 'created_at']
    search_fields = ['name', 'loadbalancer__name']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(LBPool)
class LBPoolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'loadbalancer', 'protocol', 'description', 'created_at']
    list_filter = ['protocol', 'created_at']
    search_fields = ['name', 'loadbalancer__name']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(LBMember)
class LBMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'pool', 'address', 'port', 'weight', 'is_enabled', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['address', 'pool__name']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(LBHealthMonitor)
class LBHealthMonitorAdmin(admin.ModelAdmin):
    list_display = ['id', 'pool', 'monitor_type', 'interval', 'timeout', 'retry', 'created_at']
    list_filter = ['monitor_type', 'created_at']
    search_fields = ['pool__name']
    ordering = ['-created_at']
    list_per_page = 20
