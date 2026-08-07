"""用户相关测试数据工厂"""
import uuid
from backend.models.user import Users, EmailVerification
from backend.models.authority import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority


class UserFactory:
    """用户工厂"""

    @staticmethod
    def create(user=None, password=None, nickname=None, phone=None, email=None, enable=1, **kwargs):
        """创建用户"""
        user_obj = Users.objects.create(
            user=user or f"testuser_{uuid.uuid4().hex[:8]}",
            nickname=nickname or "测试用户",
            phone=phone or "",
            email=email or "",
            enable=enable,
            **kwargs
        )
        if password:
            user_obj.set_password(password)
            user_obj.save()
        return user_obj

    @staticmethod
    def create_batch(count, **kwargs):
        """批量创建用户"""
        users = []
        for i in range(count):
            users.append(UserFactory.create(**kwargs))
        return users

    @staticmethod
    def create_admin(user="admin", password="admin123", **kwargs):
        """创建管理员用户"""
        user = UserFactory.create(user=user, password=password, **kwargs)
        # 分配管理员角色
        admin_auth = AuthorityFactory.create(authority_id=888, authority_name="超级管理员")
        UserAuthority.objects.create(user=user, authority=admin_auth)
        return user

    @staticmethod
    def create_frozen(user=None, password=None, **kwargs):
        """创建被冻结的用户"""
        return UserFactory.create(user=user, password=password, enable=2, **kwargs)


class AuthorityFactory:
    """角色工厂"""

    @staticmethod
    def create(authority_id=None, authority_name=None, parent=None, **kwargs):
        """创建角色"""
        return Authority.objects.create(
            authority_id=authority_id or 100,
            authority_name=authority_name or "测试角色",
            parent=parent,
            **kwargs
        )

    @staticmethod
    def create_batch(count, start_id=200, **kwargs):
        """批量创建角色"""
        authorities = []
        for i in range(count):
            authorities.append(AuthorityFactory.create(
                authority_id=start_id + i,
                **kwargs
            ))
        return authorities

    @staticmethod
    def create_with_menu(authority_id=None, authority_name=None, menu_count=1, **kwargs):
        """创建带菜单权限的角色"""
        authority = AuthorityFactory.create(authority_id, authority_name, **kwargs)
        for i in range(menu_count):
            menu = MenuFactory.create()
            AuthorityMenu.objects.create(authority=authority, menu=menu)
        return authority

    @staticmethod
    def create_with_button(authority_id=None, authority_name=None, button_count=1, **kwargs):
        """创建带按钮权限的角色"""
        authority = AuthorityFactory.create(authority_id, authority_name, **kwargs)
        for i in range(button_count):
            menu = MenuFactory.create()
            button = MenuButtonFactory.create(menu=menu)
            AuthorityButton.objects.create(authority=authority, menu=menu, button=button)
        return authority


class AuthorityMenuFactory:
    """角色菜单关联工厂"""

    @staticmethod
    def create(authority=None, menu=None, **kwargs):
        """创建角色菜单关联"""
        if not authority:
            authority = AuthorityFactory.create()
        if not menu:
            menu = MenuFactory.create()
        return AuthorityMenu.objects.create(
            authority=authority,
            menu=menu,
            **kwargs
        )


class AuthorityButtonFactory:
    """角色按钮权限关联工厂"""

    @staticmethod
    def create(authority=None, menu=None, button=None, **kwargs):
        """创建角色按钮权限关联"""
        if not authority:
            authority = AuthorityFactory.create()
        if not menu:
            menu = MenuFactory.create()
        if not button:
            button = MenuButtonFactory.create(menu=menu)
        return AuthorityButton.objects.create(
            authority=authority,
            menu=menu,
            button=button,
            **kwargs
        )


class MenuFactory:
    """菜单工厂"""

    @staticmethod
    def create(path=None, name=None, component=None, parent=None, **kwargs):
        """创建菜单"""
        return Menu.objects.create(
            path=path or f"/test-path-{uuid.uuid4().hex[:4]}",
            name=name or f"TestMenu{uuid.uuid4().hex[:4]}",
            component=component or "",
            parent=parent,
            **kwargs
        )


class MenuButtonFactory:
    """菜单按钮工厂"""

    @staticmethod
    def create(menu=None, name=None, desc=None, **kwargs):
        """创建菜单按钮"""
        if not menu:
            menu = MenuFactory.create()
        return MenuButton.objects.create(
            menu=menu,
            name=name or "add",
            desc=desc or "新增按钮",
            **kwargs
        )


class UserAuthorityFactory:
    """用户角色关联工厂"""

    @staticmethod
    def create(user=None, authority=None, **kwargs):
        """创建用户角色关联"""
        if not user:
            user = UserFactory.create()
        if not authority:
            authority = AuthorityFactory.create()
        return UserAuthority.objects.create(
            user=user,
            authority=authority,
            **kwargs
        )


class EmailVerificationFactory:
    """邮箱验证码工厂"""

    @staticmethod
    def create(email=None, code=None, user=None, **kwargs):
        """创建邮箱验证码"""
        from django.utils import timezone
        from datetime import timedelta

        return EmailVerification.objects.create(
            email=email or "test@example.com",
            code=code or "123456",
            user=user,
            expires_at=timezone.now() + timedelta(minutes=10),
            **kwargs
        )
