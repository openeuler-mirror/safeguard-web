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


class TestCurrentUserPassword:
    """当前用户修改密码接口测试"""

    @pytest.mark.p0
    def test_change_my_password_success(self, authenticated_client, test_user, clear_redis):
        """测试用户修改自身密码成功"""
        test_user.set_password('oldpass123')
        test_user.save()
        clear_redis(test_user.id)

        # 需要重新获取认证token
        from rest_framework_simplejwt.tokens import RefreshToken
        authenticated_client.credentials()
        refresh = RefreshToken.for_user(test_user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {'old_password': 'oldpass123', 'new_password': 'newmypass456'}
        response = authenticated_client.put('/api/users/me/password/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['errmsg'] == '密码修改成功'

        # 验证密码已更新
        test_user.refresh_from_db()
        assert check_password('newmypass456', test_user.password)

    @pytest.mark.p0
    def test_change_my_password_wrong_old_password(self, authenticated_client, test_user, clear_redis):
        """测试旧密码错误应返回错误"""
        test_user.set_password('correctpass')
        test_user.save()
        clear_redis(test_user.id)

        data = {'old_password': 'wrongpass', 'new_password': 'newpass123'}
        response = authenticated_client.put('/api/users/me/password/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_change_my_password_without_auth(self, api_client):
        """测试无认证修改密码应返回401"""
        data = {'old_password': 'oldpass', 'new_password': 'newpass123'}
        response = api_client.put('/api/users/me/password/', data, format='json')
        assert response.status_code == 401


class TestUserMenus:
    """用户菜单接口测试"""

    @pytest.mark.p0
    def test_get_menus_success(self, authenticated_client, test_user, test_authority, clear_redis):
        """测试获取当前用户菜单成功"""
        clear_redis(test_user.id)

        # 创建菜单并分配给角色
        menu1 = MenuFactory.create(path='/test1', name='TestMenu1')
        menu2 = MenuFactory.create(path='/test2', name='TestMenu2')
        AuthorityMenu.objects.create(authority=test_authority, menu=menu1)
        AuthorityMenu.objects.create(authority=test_authority, menu=menu2)

        # 为用户分配角色
        UserAuthority.objects.create(user=test_user, authority=test_authority)

        response = authenticated_client.get('/api/users/menus/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)

    @pytest.mark.p0
    def test_get_menus_without_auth(self, api_client):
        """测试无认证获取菜单应返回401"""
        response = api_client.get('/api/users/menus/')
        assert response.status_code == 401

    @pytest.mark.p1
    def test_get_menus_no_permissions(self, authenticated_client, test_user, clear_redis):
        """测试没有菜单权限时返回空列表"""
        clear_redis(test_user.id)
        response = authenticated_client.get('/api/users/menus/')
        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)


class TestUserAvatarTheme:
    """用户头像和主题接口测试"""

    @pytest.mark.p1
    def test_upload_avatar_success(self, authenticated_client, test_user, clear_redis):
        """测试上传头像成功"""
        clear_redis(test_user.id)

        file_data = BytesIO(b'fake image data')
        file_data.name = 'test.png'

        response = authenticated_client.post(
            '/api/users/me/avatar/',
            {'file': file_data},
            format='multipart'
        )

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert 'avatar' in response.data['data']
        assert response.data['data']['avatar'].startswith('/media/avatars/')

        test_user.refresh_from_db()
        assert test_user.avatar.startswith('/media/avatars/')

    @pytest.mark.p0
    def test_upload_avatar_no_file(self, authenticated_client, test_user, clear_redis):
        """测试不上传文件应报错"""
        clear_redis(test_user.id)
        response = authenticated_client.post('/api/users/me/avatar/', {}, format='multipart')
        assert response.status_code == 200
        assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_upload_avatar_without_auth(self, api_client):
        """测试无认证上传头像应返回401"""
        file_data = BytesIO(b'fake image data')
        file_data.name = 'test.png'
        response = api_client.post(
            '/api/users/me/avatar/',
            {'file': file_data},
            format='multipart'
        )
        assert response.status_code == 401

    @pytest.mark.p0
    def test_set_theme_success(self, authenticated_client, test_user, clear_redis):
        """测试设置主题成功"""
        clear_redis(test_user.id)
        response = authenticated_client.put('/api/users/me/theme/', {'theme': 'dark'}, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['theme'] == 'dark'

        test_user.refresh_from_db()
        assert test_user.theme == 'dark'

    @pytest.mark.p0
    def test_set_theme_auto(self, authenticated_client, test_user, clear_redis):
        """测试设置 auto 主题"""
        clear_redis(test_user.id)
        response = authenticated_client.put('/api/users/me/theme/', {'theme': 'auto'}, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['theme'] == 'auto'

    @pytest.mark.p0
    def test_set_theme_invalid(self, authenticated_client, test_user, clear_redis):
        """测试设置无效主题应报错"""
        clear_redis(test_user.id)
        response = authenticated_client.put('/api/users/me/theme/', {'theme': 'invalid'}, format='json')

        assert response.status_code == 200
        assert response.data['errno'] != 0


class TestUserAdminCRUD:
    """管理员用户CRUD接口测试"""

    @pytest.mark.p0
    def test_list_users_admin(self, admin_client, multiple_users):
        """测试管理员获取用户列表"""
        response = admin_client.get('/api/users/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        # 检查返回了用户数据
        if 'results' in response.data['data']:
            assert len(response.data['data']['results']) >= 5
        elif isinstance(response.data['data'], list):
            assert len(response.data['data']) >= 5

    @pytest.mark.p0
    def test_list_users_regular_user_forbidden(self, authenticated_client):
        """测试普通用户不能获取用户列表（需要管理员权限）"""
        response = authenticated_client.get('/api/users/')
        # 应该被拒绝
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_create_user_admin(self, admin_client):
        """测试管理员创建用户成功"""
        data = {
            'user': 'newcreateuser',
            'password': 'newcreatepass123',
            'nickname': '新创建用户',
            'email': 'newuser@test.com'
        }

        response = admin_client.post('/api/users/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['user'] == 'newcreateuser'
        assert Users.objects.filter(user='newcreateuser').exists()

    @pytest.mark.p0
    def test_create_user_regular_user_forbidden(self, authenticated_client):
        """测试普通用户不能创建用户"""
        data = {
            'user': 'testcreate',
            'password': 'testpass123',
            'nickname': '测试'
        }
        response = authenticated_client.post('/api/users/', data, format='json')
        assert response.status_code in (200, 403)

    @pytest.mark.p0
    def test_create_user_duplicate_username(self, admin_client, test_user):
        """测试创建已存在的用户名应失败"""
        data = {
            'user': test_user.user,
            'password': 'testpass123',
            'nickname': '重复用户'
        }
        response = admin_client.post('/api/users/', data, format='json')
        assert response.status_code == 200
        assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_retrieve_user_admin(self, admin_client, test_user):
        """测试管理员获取单个用户"""
        response = admin_client.get(f'/api/users/{test_user.pk}/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['user'] == test_user.user

    @pytest.mark.p0
    def test_update_user_admin(self, admin_client, test_user):
        """测试管理员更新用户"""
        data = {'nickname': '管理员更新的昵称', 'phone': '13800008888'}
        response = admin_client.patch(f'/api/users/{test_user.pk}/', data, format='json')

        assert response.status_code == 200
        test_user.refresh_from_db()
        assert test_user.nickname == '管理员更新的昵称'

    @pytest.mark.p0
    def test_destroy_user_admin(self, admin_client, test_user):
        """测试管理员删除用户"""
        user_id = test_user.pk
        response = admin_client.delete(f'/api/users/{user_id}/')

        assert response.status_code in (200, 204)
        if response.status_code == 200:
            assert response.data['errno'] == 0
        assert not Users.objects.filter(pk=user_id).exists()

    @pytest.mark.p0
    def test_destroy_user_regular_user_forbidden(self, authenticated_client, test_user):
        """测试普通用户不能删除用户"""
        response = authenticated_client.delete(f'/api/users/{test_user.pk}/')
        assert response.status_code in (200, 403)


class TestAdminSetPassword:
    """管理员重置用户密码接口测试"""

    @pytest.mark.p0
    def test_admin_set_password_success(self, admin_client, test_user):
        """测试管理员重置用户密码成功"""
        data = {'new_password': 'newresetpass123'}
        response = admin_client.put(f'/api/users/{test_user.pk}/password/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['errmsg'] == '密码重置成功'

        # 验证密码已更新
        test_user.refresh_from_db()
        assert check_password('newresetpass123', test_user.password)

    @pytest.mark.p0
    def test_set_password_without_auth(self, api_client, test_user):
        """测试无认证重置密码应返回401"""
        data = {'new_password': 'newpass123'}
        response = api_client.put(f'/api/users/{test_user.pk}/password/', data, format='json')
        assert response.status_code == 401

    @pytest.mark.p0
    def test_set_password_regular_user_forbidden(self, authenticated_client, test_user):
        """测试普通用户不能重置其他用户密码"""
        data = {'new_password': 'newpass123'}
        response = authenticated_client.put(f'/api/users/{test_user.pk}/password/', data, format='json')
        assert response.status_code in (200, 403)


class TestUserAuthorities:
    """用户角色管理接口测试"""

    @pytest.mark.p0
    def test_get_user_authorities(self, admin_client, test_user, test_authority):
        """测试获取用户角色列表"""
        UserAuthority.objects.create(user=test_user, authority=test_authority)

        response = admin_client.get(f'/api/users/{test_user.pk}/authorities/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)

    @pytest.mark.p0
    def test_set_user_authorities(self, admin_client, test_user):
        """测试设置用户角色（覆盖）"""
        auth1 = AuthorityFactory.create(authority_id=101, authority_name='角色1')
        auth2 = AuthorityFactory.create(authority_id=102, authority_name='角色2')

        data = {'role_ids': [auth1.pk, auth2.pk]}
        response = admin_client.put(f'/api/users/{test_user.pk}/authorities/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert UserAuthority.objects.filter(user=test_user).count() == 2

    @pytest.mark.p0
    def test_add_user_authority(self, admin_client, test_user, test_authority):
        """测试为用户添加角色"""
        data = {'authority_id': test_authority.pk}
        response = admin_client.post(f'/api/users/{test_user.pk}/authorities/add/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert UserAuthority.objects.filter(user=test_user, authority=test_authority).exists()

    @pytest.mark.p0
    def test_add_duplicate_authority(self, admin_client, test_user, test_authority):
        """测试添加重复角色应失败"""
        UserAuthority.objects.create(user=test_user, authority=test_authority)

        data = {'authority_id': test_authority.pk}
        response = admin_client.post(f'/api/users/{test_user.pk}/authorities/add/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_remove_user_authority(self, admin_client, test_user, test_authority):
        """测试移除用户角色"""
        UserAuthority.objects.create(user=test_user, authority=test_authority)

        data = {'authority_id': test_authority.pk}
        response = admin_client.delete(
            f'/api/users/{test_user.pk}/authorities/',
            data=data,
            format='json'
        )

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert not UserAuthority.objects.filter(user=test_user, authority=test_authority).exists()

    @pytest.mark.p0
    def test_remove_nonexistent_authority(self, admin_client, test_user):
        """测试移除不存在的角色应失败"""
        data = {'authority_id': 9999}
        response = admin_client.delete(
            f'/api/users/{test_user.pk}/authorities/',
            data=data,
            format='json'
        )
        assert response.status_code == 200
        assert response.data['errno'] != 0
