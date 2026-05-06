"""
Authority 模块服务层

包含角色、菜单相关的业务逻辑，供 views 层调用。
"""
from typing import Optional
from django.db import transaction
from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority


class AuthorityService:
    """角色服务"""

    @staticmethod
    def list_authorities(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """
        获取角色列表（支持分页和过滤）

        Args:
            filters: 过滤条件，如 {'authority_name__icontains': 'admin'}
            page: 页码
            page_size: 每页数量

        Returns:
            {'total': int, 'page': int, 'page_size': int, 'results': list}
        """
        queryset = Authority.objects.all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_authority(authority_id: int) -> Optional[Authority]:
        """获取角色详情"""
        try:
            return Authority.objects.get(pk=authority_id)
        except Authority.DoesNotExist:
            return None

    @staticmethod
    def create_authority(data: dict) -> Authority:
        """创建角色"""
        return Authority.objects.create(**data)

    @staticmethod
    def update_authority(authority_id: int, data: dict) -> Optional[Authority]:
        """更新角色"""
        try:
            authority = Authority.objects.get(pk=authority_id)
            for key, value in data.items():
                setattr(authority, key, value)
            authority.save()
            return authority
        except Authority.DoesNotExist:
            return None

    @staticmethod
    def delete_authority(authority_id: int) -> bool:
        """删除角色"""
        try:
            authority = Authority.objects.get(pk=authority_id)
            authority.delete()
            return True
        except Authority.DoesNotExist:
            return False

    @staticmethod
    def get_authority_menus(authority_id: int):
        """获取角色关联的菜单"""
        return Menu.objects.filter(authoritymenu__authority_id=authority_id)

    @staticmethod
    def bind_menus(authority_id: int, menu_ids: list) -> bool:
        """
        绑定角色菜单

        Args:
            authority_id: 角色ID
            menu_ids: 菜单ID列表

        Returns:
            bool: 是否成功
        """
        try:
            authority = Authority.objects.get(pk=authority_id)
            with transaction.atomic():
                # 先删除所有菜单关联
                AuthorityMenu.objects.filter(authority=authority).delete()
                # 再创建新关联
                for menu_id in menu_ids:
                    AuthorityMenu.objects.create(authority=authority, menu_id=menu_id)
            return True
        except Authority.DoesNotExist:
            return False

    @staticmethod
    def get_authority_buttons(authority_id: int):
        """获取角色关联的按钮"""
        return MenuButton.objects.filter(authority_button__authority_id=authority_id)

    @staticmethod
    def bind_buttons(authority_id: int, btn_data: list) -> bool:
        """
        绑定角色按钮权限

        Args:
            authority_id: 角色ID
            btn_data: 按钮数据列表 [{'menu_id': int, 'button_ids': [int, ...]}]

        Returns:
            bool: 是否成功
        """
        try:
            authority = Authority.objects.get(pk=authority_id)
            with transaction.atomic():
                # 先删除所有按钮关联
                AuthorityButton.objects.filter(authority=authority).delete()
                # 再创建新关联
                for item in btn_data:
                    menu_id = item.get('menu_id')
                    button_ids = item.get('button_ids', [])
                    for button_id in button_ids:
                        AuthorityButton.objects.create(
                            authority=authority,
                            menu_id=menu_id,
                            button_id=button_id
                        )
            return True
        except Authority.DoesNotExist:
            return False

    @staticmethod
    def copy_authority(authority_id: int) -> Optional[Authority]:
        """
        复制角色（包含菜单和按钮权限）

        Args:
            authority_id: 被复制的角色ID

        Returns:
            新创建的角色，或 None（如果原角色不存在）
        """
        try:
            authority = Authority.objects.get(pk=authority_id)
            with transaction.atomic():
                # 查找最大 authority_id
                max_auth = Authority.objects.order_by('-authority_id').first()
                new_authority_id = (max_auth.authority_id + 1) if max_auth else 1

                # 创建新角色
                new_authority = Authority.objects.create(
                    authority_id=new_authority_id,
                    authority_name=f'{authority.authority_name}_副本',
                    parent=authority.parent,
                    default_router=authority.default_router,
                    data_authority=authority.data_authority
                )

                # 复制菜单关联
                menu_ids = AuthorityMenu.objects.filter(authority=authority).values_list('menu_id', flat=True)
                for menu_id in menu_ids:
                    AuthorityMenu.objects.create(authority=new_authority, menu_id=menu_id)

                # 复制按钮关联
                btn_relations = AuthorityButton.objects.filter(authority=authority)
                for rel in btn_relations:
                    AuthorityButton.objects.create(
                        authority=new_authority,
                        menu=rel.menu,
                        button=rel.button
                    )

            return new_authority
        except Authority.DoesNotExist:
            return None

    @staticmethod
    def get_children(authority_id: int):
        """获取子角色"""
        return Authority.objects.filter(parent_id=authority_id)


class MenuService:
    """菜单服务"""

    @staticmethod
    def list_menus(filters: Optional[dict] = None):
        """
        获取菜单列表

        Args:
            filters: 过滤条件

        Returns:
            queryset
        """
        queryset = Menu.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.order_by('sort')

    @staticmethod
    def get_menu(menu_id: int) -> Optional[Menu]:
        """获取菜单详情"""
        try:
            return Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            return None

    @staticmethod
    def create_menu(data: dict) -> Menu:
        """创建菜单"""
        return Menu.objects.create(**data)

    @staticmethod
    def update_menu(menu_id: int, data: dict) -> Optional[Menu]:
        """更新菜单"""
        try:
            menu = Menu.objects.get(pk=menu_id)
            for key, value in data.items():
                setattr(menu, key, value)
            menu.save()
            return menu
        except Menu.DoesNotExist:
            return None

    @staticmethod
    def delete_menu(menu_id: int) -> bool:
        """删除菜单"""
        try:
            menu = Menu.objects.get(pk=menu_id)
            menu.delete()
            return True
        except Menu.DoesNotExist:
            return False

    @staticmethod
    def get_menu_tree():
        """获取完整菜单树"""
        return Menu.objects.filter(parent__isnull=True).prefetch_related('children')

    @staticmethod
    def get_user_menus(user_id: int):
        """
        获取用户可访问的菜单

        Args:
            user_id: 用户ID

        Returns:
            用户关联角色所能访问的菜单列表
        """
        authorities = Authority.objects.filter(user_authority__user_id=user_id)
        menu_ids = AuthorityMenu.objects.filter(authority__in=authorities).values_list('menu_id', flat=True)
        return Menu.objects.filter(id__in=menu_ids)

    @staticmethod
    def get_user_buttons(user_id: int, menu_id: int):
        """
        获取用户在指定菜单下的按钮权限

        Args:
            user_id: 用户ID
            menu_id: 菜单ID

        Returns:
            按钮列表
        """
        authorities = Authority.objects.filter(user_authority__user_id=user_id)
        return MenuButton.objects.filter(
            authority_button__authority__in=authorities,
            menu_id=menu_id
        )


class UserAuthorityService:
    """用户角色关联服务"""

    @staticmethod
    def get_user_authorities(user_id: int):
        """获取用户的所有角色"""
        return Authority.objects.filter(userauthority__user_id=user_id)

    @staticmethod
    def set_user_roles(user_id: int, role_ids: list) -> bool:
        """
        设置用户角色（覆盖式）

        Args:
            user_id: 用户ID
            role_ids: 角色ID列表

        Returns:
            bool: 是否成功
        """
        from backend.models import Users
        try:
            user = Users.objects.get(pk=user_id)
            with transaction.atomic():
                # 先删除所有角色关联
                UserAuthority.objects.filter(user=user).delete()
                # 再创建新关联
                for role_id in role_ids:
                    UserAuthority.objects.create(user=user, authority_id=role_id)
            return True
        except Users.DoesNotExist:
            return False

    @staticmethod
    def add_user_authority(user_id: int, authority_id: int) -> Optional[UserAuthority]:
        """为用户添加角色"""
        from backend.models import Users
        try:
            user = Users.objects.get(pk=user_id)
            authority = Authority.objects.get(pk=authority_id)
            return UserAuthority.objects.get_or_create(user=user, authority=authority)
        except (Users.DoesNotExist, Authority.DoesNotExist):
            return None

    @staticmethod
    def remove_user_authority(user_id: int, authority_id: int) -> bool:
        """移除用户角色"""
        try:
            ua = UserAuthority.objects.get(user_id=user_id, authority_id=authority_id)
            ua.delete()
            return True
        except UserAuthority.DoesNotExist:
            return False
