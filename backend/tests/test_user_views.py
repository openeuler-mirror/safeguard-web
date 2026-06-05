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

        # 清除Redis缓存，避免测试间数据污染
        _clear_user_redis(self.user.id)
        _clear_user_redis(self.admin_user.id)

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


def _clear_user_redis(user_id):
    """清除 Redis 中缓存的用户数据"""
    redis_client.delete(f'user:{user_id}')


class UsersViewSetAvatarThemeTest(APITestCase):
    """头像和主题相关测试"""

    def setUp(self):
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        _clear_user_redis(self.user.id)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_upload_avatar_success(self):
        """测试上传头像"""
        from io import BytesIO
        file_data = BytesIO(b'fake image data')
        file_data.name = 'test.png'
        response = self.client.post(
            '/api/users/me/avatar/',
            {'file': file_data},
            format='multipart'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('avatar', response.data['data'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.startswith('/media/avatars/'))

    def test_upload_avatar_no_file(self):
        """测试不上传文件应报错"""
        response = self.client.post('/api/users/me/avatar/', {}, format='multipart')
        self.assertNotEqual(response.data['errno'], 0)

    def test_set_theme_success(self):
        """测试设置主题"""
        response = self.client.put('/api/users/me/theme/', {'theme': 'dark'}, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['theme'], 'dark')
        self.user.refresh_from_db()
        self.assertEqual(self.user.theme, 'dark')

    def test_set_theme_invalid(self):
        """测试设置无效主题应报错"""
        response = self.client.put('/api/users/me/theme/', {'theme': 'invalid'}, format='json')
        self.assertNotEqual(response.data['errno'], 0)

    def test_set_theme_auto(self):
        """测试设置 auto 主题"""
        response = self.client.put('/api/users/me/theme/', {'theme': 'auto'}, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['theme'], 'auto')


class UsersViewSetImportExportTest(APITestCase):
    """批量导入导出测试"""

    def setUp(self):
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.admin_user = Users.objects.create(
            user='admin',
            password='adminpass123',
            nickname='管理员'
        )
        UserAuthority.objects.create(user=self.admin_user, authority=self.admin_auth)

        _clear_user_redis(self.admin_user.id)
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_import_users_success(self):
        """测试批量导入用户"""
        import openpyxl
        from io import BytesIO

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['user', 'nickname', 'phone', 'email', 'enable', 'theme', 'password'])
        ws.append(['importuser1', '导入用户1', '13800138001', 'import1@test.com', 1, 'light', 'pass123'])
        ws.append(['importuser2', '导入用户2', '13800138002', 'import2@test.com', 1, 'dark', 'pass456'])
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = self.client.post(
            '/api/users/import/',
            {'file': buffer},
            format='multipart'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('created', response.data['data'])
        self.assertEqual(response.data['data']['created'], 2)
        self.assertTrue(Users.objects.filter(user='importuser1').exists())
        self.assertTrue(Users.objects.filter(user='importuser2').exists())

    def test_import_users_update_existing(self):
        """测试导入已存在用户时应更新"""
        import openpyxl
        from io import BytesIO

        Users.objects.create(user='existing', password='oldpass', nickname='旧昵称')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['user', 'nickname'])
        ws.append(['existing', '新昵称'])
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = self.client.post(
            '/api/users/import/',
            {'file': buffer},
            format='multipart'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['updated'], 1)
        user = Users.objects.get(user='existing')
        self.assertEqual(user.nickname, '新昵称')

    def test_import_users_no_file(self):
        """测试不上传文件应报错"""
        response = self.client.post('/api/users/import/', {}, format='multipart')
        self.assertNotEqual(response.data['errno'], 0)

    def test_export_users(self):
        """测试导出用户"""
        Users.objects.create(user='u1', password='p1', nickname='用户1')
        Users.objects.create(user='u2', password='p2', nickname='用户2')

        response = self.client.get('/api/users/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])

