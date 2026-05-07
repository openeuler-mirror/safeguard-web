"""基础权限类"""
from rest_framework import permissions


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
