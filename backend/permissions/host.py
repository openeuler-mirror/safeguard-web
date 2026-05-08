"""主机模块权限类"""
from backend.permissions.base import DataScopePermission


class HostPermission(DataScopePermission):
    """主机模块权限类"""

    def has_object_permission(self, request, view, obj):
        # TODO: 关联用户Authority的数据权限范围
        return True