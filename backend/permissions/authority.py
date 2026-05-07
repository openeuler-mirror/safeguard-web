"""权限相关权限类"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    超级管理员权限校验

    检查用户是否拥有超级管理员角色（authority_id=888）
    """

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        # 检查用户是否有超级管理员角色
        from backend.models import UserAuthority
        return UserAuthority.objects.filter(
            user_id=request.user.id,
            authority__authority_id=888
        ).exists()


class IsAdmin(permissions.BasePermission):
    """
    管理员权限校验

    检查用户是否拥有管理员角色（authority_id=888 或 889）
    """

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        # 检查用户是否有管理员角色
        from backend.models import UserAuthority
        return UserAuthority.objects.filter(
            user_id=request.user.id,
            authority__authority_id__in=[888, 889]
        ).exists()


class AuthorityPermission(permissions.BasePermission):
    """
    角色权限校验

    检查用户是否拥有访问 authority 相关资源的权限。
    """

    def has_permission(self, request, view):
        """检查是否有权限访问视图"""
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """检查是否有权限访问具体对象"""
        return True
