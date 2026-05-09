from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

from backend.models import Users
from backend.models import Authority, UserAuthority


class UsersViewSetTest(APITestCase):
    """UsersViewSet 视图集测试（含JWT认证）"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户',
            phone='13800138000',
            email='test@example.com'
        )
        # 创建管理员角色
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        # 创建管理员用户并分配角色
        self.admin_user = Users.objects.create(
            user='admin',
            password='adminpass123',
            nickname='管理员',
            enable=1
        )
        # 分配管理员角色
        UserAuthority.objects.create(user=self.admin_user, authority=self.admin_auth)

        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_client = self.client.__class__()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')

    def test_me_get_success(self):
        """测试GET /me/ 获取当前用户信息"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['user'], 'testuser')
        self.assertEqual(response.data['data']['nickname'], '测试用户')
        self.assertIn('uuid', response.data['data'])

    def test_me_get_without_auth(self):
        """测试GET /me/ 无认证应返回401"""
        client = self.client.__class__()
        response = client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get_invalid_token(self):
        """测试GET /me/ 无效token应返回401"""
        client = self.client.__class__()
        client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_put_success(self):
        """测试PUT /me/ 更新当前用户信息"""
        data = {'nickname': '新昵称', 'phone': '13900001111'}
        response = self.client.put('/api/users/me/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['nickname'], '新昵称')
        self.assertEqual(response.data['data']['phone'], '13900001111')

    def test_me_put_partial_update(self):
        """测试PATCH /me/ 部分更新"""
        data = {'nickname': '部分更新'}
        response = self.client.put('/api/users/me/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['nickname'], '部分更新')

    def test_me_put_invalid_data(self):
        """测试PUT /me/ 无效数据应返回错误"""
        data = {'email': 'not-an-email'}
        response = self.client.put('/api/users/me/', data, format='json')
        self.assertNotEqual(response.data['errno'], 0)

    def test_set_password_success(self):
        """测试管理员重置用户密码"""
        data = {'new_password': 'newresetpass123'}
        response = self.admin_client.put(f'/api/users/{self.user.pk}/password/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['errmsg'], '密码重置成功')
        # 验证密码已更新
        self.user.refresh_from_db()
        self.assertTrue(check_password('newresetpass123', self.user.password))

    def test_set_password_without_auth(self):
        """测试重置密码无认证应返回401"""
        client = self.client.__class__()
        data = {'new_password': 'newpass123'}
        response = client.put(f'/api/users/{self.user.pk}/password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_my_password_success(self):
        """测试用户修改自身密码"""
        self.user.set_password('oldpass123')
        self.user.save()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {'old_password': 'oldpass123', 'new_password': 'newmypass456'}
        response = self.client.put('/api/users/me/password/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['errmsg'], '密码修改成功')

    def test_change_my_password_wrong_old_password(self):
        """测试修改密码旧密码错误应返回错误"""
        data = {'old_password': 'wrongoldpass', 'new_password': 'newpass123'}
        response = self.client.put('/api/users/me/password/', data, format='json')
        self.assertNotEqual(response.data['errno'], 0)

    def test_change_my_password_without_auth(self):
        """测试修改密码无认证应返回401"""
        client = self.client.__class__()
        data = {'old_password': 'oldpass', 'new_password': 'newpass123'}
        response = client.put('/api/users/me/password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_role_not_implemented(self):
        """测试设置角色返回404"""
        data = {'role': 'admin'}
        response = self.admin_client.put(f'/api/users/{self.user.pk}/role/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_users(self):
        """测试列出用户列表"""
        response = self.admin_client.get('/api/users/')
        self.assertEqual(response.data['errno'], 0)

    def test_create_user(self):
        """测试创建新用户"""
        data = {
            'user': 'newcreateuser',
            'password': 'newcreatepass123',
            'nickname': '新创建用户'
        }
        response = self.admin_client.post('/api/users/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['user'], 'newcreateuser')

    def test_retrieve_user(self):
        """测试获取单个用户"""
        response = self.client.get(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['user'], 'testuser')

    def test_destroy_user(self):
        """测试删除用户"""
        response = self.admin_client.delete(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(Users.objects.filter(pk=self.user.pk).exists())


from backend.authentication import redis_client


