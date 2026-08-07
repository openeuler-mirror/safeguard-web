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


class TestSendVerificationCodeView:
    """发送邮箱验证码接口测试"""

    @patch("backend.views.auth.send_mail")
    @patch("safeguard_web.settings.IS_LOCAL", new=False)
    def test_send_code_for_register_success(self, mock_send_mail, api_client):
        """测试发送注册验证码成功"""
        url = "/api/auth/send-code/"
        data = {
            "email": "register@example.com",
            "purpose": "register"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        assert EmailVerification.objects.filter(email="register@example.com").exists()

    @patch("safeguard_web.settings.IS_LOCAL", new=True)
    def test_send_code_local_mode(self, api_client):
        """测试本地模式发送验证码"""
        url = "/api/auth/send-code/"
        data = {
            "email": "local@example.com",
            "purpose": "register"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        assert "local_verify_url" in response.data["data"]
        assert "code" in response.data["data"]

    def test_send_code_for_register_email_exists(self, api_client, test_user):
        """测试注册时邮箱已存在"""
        test_user.email = "exists@example.com"
        test_user.save()

        url = "/api/auth/send-code/"
        data = {
            "email": "exists@example.com",
            "purpose": "register"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_send_code_for_forgot_password_success(self, api_client, test_user):
        """测试发送忘记密码验证码成功"""
        test_user.email = "forgot@example.com"
        test_user.save()

        url = "/api/auth/send-code/"
        data = {
            "email": "forgot@example.com",
            "purpose": "forgot"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0

    def test_send_code_for_forgot_password_email_not_found(self, api_client):
        """测试忘记密码时邮箱不存在"""
        url = "/api/auth/send-code/"
        data = {
            "email": "notfound@example.com",
            "purpose": "forgot"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0


class TestVerifyCodeView:
    """验证邮箱验证码接口测试"""

    def test_verify_code_success(self, api_client):
        """测试验证验证码成功"""
        EmailVerificationFactory.create(
            email="verify@example.com",
            code="123456",
            used=False,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = "/api/auth/verify-code/"
        data = {
            "email": "verify@example.com",
            "code": "123456"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0
        verification = EmailVerification.objects.get(email="verify@example.com", code="123456")
        assert verification.used is True

    def test_verify_code_failed_wrong_code(self, api_client):
        """测试验证码错误"""
        EmailVerificationFactory.create(
            email="verify2@example.com",
            code="123456",
            used=False
        )

        url = "/api/auth/verify-code/"
        data = {
            "email": "verify2@example.com",
            "code": "654321"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_verify_code_failed_expired(self, api_client):
        """测试验证码已过期"""
        EmailVerificationFactory.create(
            email="expired@example.com",
            code="123456",
            used=False,
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        url = "/api/auth/verify-code/"
        data = {
            "email": "expired@example.com",
            "code": "123456"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_verify_code_failed_already_used(self, api_client):
        """测试验证码已使用"""
        EmailVerificationFactory.create(
            email="used@example.com",
            code="123456",
            used=True
        )

        url = "/api/auth/verify-code/"
        data = {
            "email": "used@example.com",
            "code": "123456"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0


class TestResetPasswordView:
    """通过验证码重置密码接口测试"""

    def test_reset_password_success(self, api_client, test_user):
        """测试重置密码成功"""
        test_user.email = "reset@example.com"
        test_user.save()

        verification = EmailVerificationFactory.create(
            email="reset@example.com",
            code="123456",
            user=test_user,
            used=False,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = "/api/auth/reset-password/"
        data = {
            "email": "reset@example.com",
            "code": "123456",
            "new_password": "newpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] == 0

        # 验证密码已更新
        test_user.refresh_from_db()
        from django.contrib.auth.hashers import check_password
        assert check_password("newpassword123", test_user.password)

        # 验证验证码已使用
        verification.refresh_from_db()
        assert verification.used is True

    def test_reset_password_failed_wrong_code(self, api_client, test_user):
        """测试验证码错误重置失败"""
        test_user.email = "reset2@example.com"
        test_user.save()

        EmailVerificationFactory.create(
            email="reset2@example.com",
            code="123456",
            user=test_user,
            used=False
        )

        url = "/api/auth/reset-password/"
        data = {
            "email": "reset2@example.com",
            "code": "654321",
            "new_password": "newpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0

    def test_reset_password_failed_expired_code(self, api_client, test_user):
        """测试验证码过期重置失败"""
        test_user.email = "reset3@example.com"
        test_user.save()

        EmailVerificationFactory.create(
            email="reset3@example.com",
            code="123456",
            user=test_user,
            used=False,
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        url = "/api/auth/reset-password/"
        data = {
            "email": "reset3@example.com",
            "code": "123456",
            "new_password": "newpassword123"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data["errno"] != 0


class TestLocalVerifyView:
    """本地验证页面测试"""

    def test_local_verify_success(self, api_client):
        """测试本地验证页面显示验证码"""
        EmailVerificationFactory.create(
            email="local@example.com",
            code="123456",
            used=False,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = f"/api/auth/local-verify/local@example.com/123456/"
        response = api_client.get(url)

        assert response.status_code == 200
        assert "123456" in response.content.decode()

    def test_local_verify_failed(self, api_client):
        """测试本地验证页面显示失败"""
        url = "/api/auth/local-verify/invalid@example.com/999999/"
        response = api_client.get(url)

        assert response.status_code == 200
        assert "验证码已失效" in response.content.decode()


class TestJWTAuthentication:
    """JWT 认证测试"""

    def test_access_protected_route_without_token(self, api_client):
        """测试未认证访问受保护路由"""
        url = "/api/users/me/"
        response = api_client.get(url)

        assert response.status_code == 401

    def test_access_protected_route_with_token(self, authenticated_client, test_user):
        """测试已认证访问受保护路由"""
        url = "/api/users/me/"
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.data["errno"] == 0

    def test_access_protected_route_with_invalid_token(self, api_client):
        """测试使用无效 token 访问"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')

        url = "/api/users/me/"
        response = api_client.get(url)

        assert response.status_code == 401
