"""基础权限类"""
from rest_framework import permissions


class DataScopePermission(permissions.BasePermission):
    """
    数据级权限基类

    基于用户的 Authority.data_authority 实现行级数据过滤。
    通过递归收集用户角色的 data_authority 链，确定数据可见范围。
    """

    def has_permission(self, request, view):
        """检查是否有权限访问视图"""
        return True

    def has_object_permission(self, request, view, obj):
        """检查是否有权限访问具体对象"""
        return self.has_data_scope_permission(request, view, obj)

    def has_data_scope_permission(self, request, view, obj):
        """
        默认放行，子类可覆写
        """
        return True

    @staticmethod
    def _is_super_admin(user_id):
        """检查用户是否为超级管理员（authority_id=888）"""
        from backend.models import UserAuthority
        return UserAuthority.objects.filter(
            user_id=user_id, authority__authority_id=888
        ).exists()

    @staticmethod
    def get_data_scope_authority_ids(user_id):
        """
        获取用户数据权限范围内的所有 authority_id（含自身角色及递归 data_authority 链）

        Returns:
            set: authority_id 集合
        """
        from backend.models import UserAuthority, Authority

        # 获取用户直接拥有的角色
        direct_ids = set(
            UserAuthority.objects.filter(user_id=user_id)
            .values_list('authority__authority_id', flat=True)
        )

        # 递归收集 data_authority 链
        def _collect_data_scope(start_ids):
            result = set(start_ids)
            queue = list(start_ids)
            while queue:
                current = queue.pop(0)
                # 查找 current 对应的 Authority 的 data_authority
                auth = Authority.objects.filter(authority_id=current).first()
                if auth and auth.data_authority_id:
                    data_auth_id = auth.data_authority_id
                    if data_auth_id not in result:
                        result.add(data_auth_id)
                        queue.append(data_auth_id)
            return result

        return _collect_data_scope(direct_ids)

    @staticmethod
    def get_data_scope_user_ids(user_id):
        """
        获取数据权限范围内所有用户的 id

        即：拥有该用户任一角色（含 data_authority 链上角色）的用户列表
        """
        from backend.models import UserAuthority

        authority_ids = DataScopePermission.get_data_scope_authority_ids(user_id)
        user_ids = set(
            UserAuthority.objects.filter(authority__authority_id__in=authority_ids)
            .values_list('user_id', flat=True)
        )
        return user_ids

    @staticmethod
    def filter_queryset(queryset, user_id):
        """
        对 queryset 应用数据权限过滤

        超级管理员不过滤；其他用户仅能看到 created_by 在数据权限范围内的数据。
        """
        if DataScopePermission._is_super_admin(user_id):
            return queryset

        scope_user_ids = DataScopePermission.get_data_scope_user_ids(user_id)
        # 包含自己创建的数据
        scope_user_ids.add(user_id)
        return queryset.filter(created_by_id__in=scope_user_ids)
