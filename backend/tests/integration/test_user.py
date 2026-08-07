"""用户管理模块集成测试"""
import pytest
from unittest.mock import patch
from io import BytesIO
from django.contrib.auth.hashers import check_password

from backend.models.user import Users
from backend.models.authority import Authority, UserAuthority, Menu, AuthorityMenu
from backend.tests.factories.user_factories import (
    UserFactory, AuthorityFactory, MenuFactory, UserAuthorityFactory
)

pytestmark = pytest.mark.django_db


class TestCurrentUserMe:
    """当前用户信息接口测试"""

    @pytest.mark.p0
    def test_me_get_success(self, authenticated_client, test_user):
        """测试获取当前用户信息成功"""
        response = authenticated_client.get('/api/users/me/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['user'] == test_user.user
        assert response.data['data']['nickname'] == test_user.nickname
        assert 'uuid' in response.data['data']

    @pytest.mark.p0
    def test_me_get_without_auth(self, api_client):
        """测试无认证获取当前用户信息应返回401"""
        response = api_client.get('/api/users/me/')
        assert response.status_code == 401

    @pytest.mark.p0
    def test_me_get_invalid_token(self, api_client):
        """测试无效token应返回401"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = api_client.get('/api/users/me/')
        assert response.status_code == 401

    @pytest.mark.p0
    def test_me_put_success(self, authenticated_client, test_user, clear_redis):
        """测试更新当前用户信息成功"""
        clear_redis(test_user.id)
        data = {'nickname': '新昵称', 'phone': '13900001111', 'email': 'newemail@test.com'}

        response = authenticated_client.put('/api/users/me/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['nickname'] == '新昵称'
        assert response.data['data']['phone'] == '13900001111'

        test_user.refresh_from_db()
        assert test_user.nickname == '新昵称'
        assert test_user.phone == '13900001111'

    @pytest.mark.p0
    def test_me_put_partial_update(self, authenticated_client, test_user, clear_redis):
        """测试部分更新当前用户信息"""
        clear_redis(test_user.id)
        data = {'nickname': '部分更新'}

        response = authenticated_client.put('/api/users/me/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['nickname'] == '部分更新'

    @pytest.mark.p0
    def test_me_put_invalid_email(self, authenticated_client, test_user, clear_redis):
        """测试无效邮箱应返回错误"""
        clear_redis(test_user.id)
        data = {'email': 'not-an-email'}

        response = authenticated_client.put('/api/users/me/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] != 0
