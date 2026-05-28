from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models import Users, Authority, Menu
from backend.serializers.authority import SetUserRoleSerializer


class SetUserRoleSerializerTest(TestCase):
    """SetUserRoleSerializer 测试"""

    def test_valid_role_ids(self):
        """测试有效角色ID列表"""
        data = {'role_ids': [1, 2, 3]}
        serializer = SetUserRoleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_empty_role_ids(self):
        """测试空角色ID列表"""
        data = {'role_ids': []}
        serializer = SetUserRoleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_role_ids(self):
        """测试缺少role_ids"""
        data = {}
        serializer = SetUserRoleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role_ids', serializer.errors)

    def test_invalid_role_ids_type(self):
        """测试role_ids类型错误"""
        data = {'role_ids': 'not_a_list'}
        serializer = SetUserRoleSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_role_ids_with_non_integer(self):
        """测试role_ids包含非整数"""
        data = {'role_ids': [1, 'abc', 3]}
        serializer = SetUserRoleSerializer(data=data)
        self.assertFalse(serializer.is_valid())


# ============ Authority ViewSet 测试 ============

from backend.views.authority import AuthorityViewSet, MenuViewSet


class AuthorityViewSetTest(APITestCase):
    """AuthorityViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.superuser = Users.objects.create(
            user='superuser',
            password='superpass123',
            nickname='超级用户'
        )
        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_authorities(self):
        """测试列出角色"""
        Authority.objects.create(authority_id=1, authority_name='管理员')
        Authority.objects.create(authority_id=2, authority_name='普通用户')
        response = self.client.get('/api/authority/authorities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_authority(self):
        """测试创建角色"""
        data = {
            'authority_id': 1,
            'authority_name': '新角色',
            'default_router': '/home'
        }
        response = self.client.post('/api/authority/authorities/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['authority_name'], '新角色')

    def test_create_authority_duplicate_id(self):
        """测试创建角色ID重复"""
        Authority.objects.create(authority_id=1, authority_name='管理员')
        data = {'authority_id': 1, 'authority_name': '另一个角色'}
        response = self.client.post('/api/authority/authorities/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_authority(self):
        """测试获取单个角色"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        response = self.client.get(f'/api/authority/authorities/{auth.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['authority_name'], '管理员')

    def test_update_authority(self):
        """测试更新角色"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        data = {'authority_name': '超级管理员'}
        response = self.client.put(f'/api/authority/authorities/{auth.pk}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['authority_name'], '超级管理员')

    def test_partial_update_authority(self):
        """测试部分更新角色"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        data = {'default_router': '/dashboard'}
        response = self.client.patch(f'/api/authority/authorities/{auth.pk}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['default_router'], '/dashboard')

    def test_delete_authority(self):
        """测试删除角色"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        response = self.client.delete(f'/api/authority/authorities/{auth.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Authority.objects.filter(pk=auth.pk).exists())

    def test_get_authority_menus(self):
        """测试获取角色菜单"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        AuthorityMenu.objects.create(authority=auth, menu=menu)
        response = self.client.get(f'/api/authority/authorities/{auth.pk}/menus/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_bind_authority_menus(self):
        """测试绑定角色菜单"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        menu1 = Menu.objects.create(path='/users', name='Users', sort=1)
        menu2 = Menu.objects.create(path='/roles', name='Roles', sort=2)
        data = {'menu_ids': [menu1.pk, menu2.pk]}
        response = self.client.put(f'/api/authority/authorities/{auth.pk}/menus/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AuthorityMenu.objects.filter(authority=auth).count(), 2)

    def test_bind_authority_menus_keeps_existing_bindings_on_invalid_menu(self):
        auth = Authority.objects.create(authority_id=1, authority_name='admin')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        AuthorityMenu.objects.create(authority=auth, menu=menu)

        response = self.client.put(
            f'/api/authority/authorities/{auth.pk}/menus/',
            {'menu_ids': [menu.pk, 999999]},
            format='json',
        )

        self.assertNotEqual(response.data['errno'], 0)
        self.assertEqual(
            list(AuthorityMenu.objects.filter(authority=auth).values_list('menu_id', flat=True)),
            [menu.pk],
        )

    def test_get_authority_buttons(self):
        """测试获取角色按钮权限"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        btn = MenuButton.objects.create(menu=menu, name='add', desc='添加')
        AuthorityButton.objects.create(authority=auth, menu=menu, button=btn)
        response = self.client.get(f'/api/authority/authorities/{auth.pk}/btns/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_bind_authority_buttons(self):
        """测试绑定角色按钮权限"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        btn1 = MenuButton.objects.create(menu=menu, name='add')
        btn2 = MenuButton.objects.create(menu=menu, name='edit')
        data = {
            'buttons': [
                {'menu_id': menu.pk, 'button_ids': [btn1.pk, btn2.pk]}
            ]
        }
        response = self.client.put(f'/api/authority/authorities/{auth.pk}/btns/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AuthorityButton.objects.filter(authority=auth).count(), 2)

    def test_bind_authority_buttons_keeps_existing_bindings_on_invalid_button(self):
        auth = Authority.objects.create(authority_id=1, authority_name='admin')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        btn = MenuButton.objects.create(menu=menu, name='add')
        AuthorityButton.objects.create(authority=auth, menu=menu, button=btn)

        response = self.client.put(
            f'/api/authority/authorities/{auth.pk}/btns/',
            {'buttons': [{'menu_id': menu.pk, 'button_ids': [btn.pk, 999999]}]},
            format='json',
        )

        self.assertNotEqual(response.data['errno'], 0)
        self.assertEqual(
            list(AuthorityButton.objects.filter(authority=auth).values_list('button_id', flat=True)),
            [btn.pk],
        )

    def test_copy_authority(self):
        """测试复制角色"""
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        AuthorityMenu.objects.create(authority=auth, menu=menu)
        response = self.client.post(f'/api/authority/authorities/{auth.pk}/copy/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(Authority.objects.count(), 2)

    def test_authority_unauthorized(self):
        """测试未授权访问"""
        client = self.client.__class__()
        response = client.get('/api/authority/authorities/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


