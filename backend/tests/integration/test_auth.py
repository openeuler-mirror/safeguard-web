"""认证授权模块集成测试"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta

from backend.models.user import Users, EmailVerification
from backend.models.authority import Authority, UserAuthority
from backend.tests.factories.user_factories import (
    UserFactory, AuthorityFactory, EmailVerificationFactory, UserAuthorityFactory
)

pytestmark = pytest.mark.django_db


class TestLoginView:
    """用户登录接口测试"""

    def test_login_success_with_username(self, api_client, test_user):
        """测试使用用户名登录成功"""
        test_user.set_password("testpass123")
        test_user.save()

        url = "/api/auth/login/"
        data = {
            "username": test_user.user,
            "password": "testpass123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]

    def test_login_success_with_email(self, api_client):
        """测试使用邮箱登录成功"""
        user = UserFactory.create(email="testlogin@example.com", password="testpass123")

        url = "/api/auth/login/"
        data = {
            "username": "testlogin@example.com",
            "password": "testpass123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0

    def test_login_failed_wrong_password(self, api_client, test_user):
        """测试密码错误登录失败"""
        test_user.set_password("correctpass")
        test_user.save()

        url = "/api/auth/login/"
        data = {
            "username": test_user.user,
            "password": "wrongpass"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_login_failed_user_not_exist(self, api_client):
        """测试用户不存在登录失败"""
        url = "/api/auth/login/"
        data = {
            "username": "nonexistent",
            "password": "anypass"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_login_failed_user_disabled(self, api_client, test_user):
        """测试被禁用用户登录失败"""
        test_user.set_password("testpass123")
        test_user.enable = 2
        test_user.save()

        url = "/api/auth/login/"
        data = {
            "username": test_user.user,
            "password": "testpass123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_login_failed_missing_parameters(self, api_client):
        """测试缺少必要参数"""
        url = "/api/auth/login/"

        # 缺少密码
        response = api_client.post(url, {"username": "test"}, format="json")
        assert response.status_code == 200
        assert response.data["errno"] != 0


class TestRegisterView:
    """用户注册接口测试"""

    def test_register_success(self, api_client):
        """测试注册成功"""
        url = "/api/auth/register/"
        data = {
            "user": "newuser001",
            "password": "password123",
            "nickname": "新用户",
            "email": "newuser@example.com"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        assert response.data["data"]["user"] == "newuser001"
        assert Users.objects.filter(user="newuser001").exists()

    def test_register_failed_user_already_exists(self, api_client, test_user):
        """测试用户名已存在注册失败"""
        url = "/api/auth/register/"
        data = {
            "user": test_user.user,
            "password": "password123"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_register_failed_password_too_short(self, api_client):
        """测试密码太短注册失败"""
        url = "/api/auth/register/"
        data = {
            "user": "newuser002",
            "password": "12345"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_register_failed_missing_user(self, api_client):
        """测试缺少用户名注册失败"""
        url = "/api/auth/register/"
        data = {
            "password": "password123"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_register_failed_missing_password(self, api_client):
        """测试缺少密码注册失败"""
        url = "/api/auth/register/"
        data = {
            "user": "newuser003"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_register_auto_assign_default_role(self, api_client):
        """测试注册时自动分配默认角色"""
        # 先创建默认角色
        from safeguard_web.settings import DEFAULT_USER_AUTHORITY_ID
        Authority.objects.create(authority_id=DEFAULT_USER_AUTHORITY_ID, authority_name="普通用户")

        url = "/api/auth/register/"
        data = {
            "user": "userwithrole",
            "password": "password123"
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        user = Users.objects.get(user="userwithrole")
        assert UserAuthority.objects.filter(user=user).exists()
