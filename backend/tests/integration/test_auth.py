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
