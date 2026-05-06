from django.contrib import admin
from backend.models import Users, EmailVerification, Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority


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


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ['authority_id', 'authority_name', 'parent', 'default_router', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['authority_id', 'authority_name']
    ordering = ['authority_id']
    raw_id_fields = ['parent', 'data_authority']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'path', 'parent', 'sort', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'path']
    ordering = ['sort', 'id']
    raw_id_fields = ['parent']


@admin.register(MenuButton)
class MenuButtonAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc', 'menu', 'created_at']
    list_filter = ['menu', 'created_at']
    search_fields = ['name', 'desc']
    raw_id_fields = ['menu']


@admin.register(AuthorityMenu)
class AuthorityMenuAdmin(admin.ModelAdmin):
    list_display = ['authority', 'menu', 'created_at']
    list_filter = ['authority', 'created_at']
    raw_id_fields = ['authority', 'menu']


@admin.register(AuthorityButton)
class AuthorityButtonAdmin(admin.ModelAdmin):
    list_display = ['authority', 'menu', 'button', 'created_at']
    list_filter = ['authority', 'created_at']
    raw_id_fields = ['authority', 'menu', 'button']


@admin.register(UserAuthority)
class UserAuthorityAdmin(admin.ModelAdmin):
    list_display = ['user', 'authority', 'created_at']
    list_filter = ['authority', 'created_at']
    raw_id_fields = ['user', 'authority']
