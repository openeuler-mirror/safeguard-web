"""用户相关 Admin 配置"""
from django.contrib import admin
from backend.models import Users, EmailVerification


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nickname', 'email', 'phone', 'enable', 'created_at']
    list_filter = ['enable', 'created_at']
    search_fields = ['user', 'nickname', 'email', 'phone']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'user', 'code', 'used', 'expires_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['email', 'code']
    ordering = ['-created_at']
    list_per_page = 20
