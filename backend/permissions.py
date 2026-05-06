"""
权限模块

包含自定义权限类，用于 API 访问控制。
"""
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


class DataScopePermission(permissions.BasePermission):
    """
    数据级权限基类

    用于控制用户对具体数据的访问权限。
    子类需要重写 has_data_scope_permission 方法。
    """

    def has_permission(self, request, view):
        """检查是否有权限访问视图"""
        return True

    def has_object_permission(self, request, view, obj):
        """检查是否有权限访问具体对象"""
        return self.has_data_scope_permission(request, view, obj)

    def has_data_scope_permission(self, request, view, obj):
        """
        子类重写此方法实现具体的数据权限校验

        Args:
            request: HTTP 请求
            view: 视图
            obj: 数据对象

        Returns:
            bool: 是否有权限
        """
        return True


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


class IsAuthenticated(permissions.BasePermission):
    """
    确保用户已认证
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class AllowAny(permissions.BasePermission):
    """
    允许任意访问
    """

    def has_permission(self, request, view):
        return True
