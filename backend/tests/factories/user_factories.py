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
    def create_admin(user="admin", password="admin123", **kwargs):
        """创建管理员用户"""
        user = UserFactory.create(user=user, password=password, **kwargs)
        # 分配管理员角色
        admin_auth = AuthorityFactory.create(authority_id=888, authority_name="超级管理员")
        UserAuthority.objects.create(user=user, authority=admin_auth)
        return user
