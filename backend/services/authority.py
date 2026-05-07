"""权限相关服务"""
from typing import Optional
from django.db import transaction
from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton


class AuthorityService:
    """角色服务"""

    @staticmethod
    def list_authorities(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取角色列表（支持分页和过滤）"""
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
        """绑定角色菜单"""
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
        """绑定角色按钮权限"""
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
        """复制角色（包含菜单和按钮权限）"""
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
        """获取菜单列表"""
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
        """获取用户可访问的菜单"""
        authorities = Authority.objects.filter(user_authority__user_id=user_id)
        menu_ids = AuthorityMenu.objects.filter(authority__in=authorities).values_list('menu_id', flat=True)
        return Menu.objects.filter(id__in=menu_ids)

    @staticmethod
    def get_user_buttons(user_id: int, menu_id: int):
        """获取用户在指定菜单下的按钮权限"""
        authorities = Authority.objects.filter(user_authority__user_id=user_id)
        return MenuButton.objects.filter(
            authority_button__authority__in=authorities,
            menu_id=menu_id
        )
