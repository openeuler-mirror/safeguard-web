"""数据权限类"""
from rest_framework import permissions


class DataScopePermission(permissions.BasePermission):
    """
    数据范围权限基类

    基于用户的 Authority.data_authority 实现行级数据过滤
    子类可覆写 get_data_scope_filter 方法自定义过滤逻辑
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """默认放行，子类可覆写"""
        return True

    @staticmethod
    def get_data_scope_filter(user):
        """
        获取当前用户的数据范围过滤条件

        Returns:
            dict: 可用于 QuerySet.filter(**filter) 的字典
        """
        # TODO: 根据用户角色的 data_authority 字段生成过滤条件
        # 当前默认返回空字典（不过滤）
        return {}
