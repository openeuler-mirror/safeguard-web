from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Menu


class MenuViewSetTest(APITestCase):
    """MenuViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_menus(self):
        """测试列出菜单"""
        Menu.objects.create(path='/users', name='Users', sort=1)
        Menu.objects.create(path='/roles', name='Roles', sort=2)
        response = self.client.get('/api/authority/menus/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['count'], 2)

    def test_create_menu(self):
        """测试创建菜单"""
        data = {
            'path': '/newmenu',
            'name': 'NewMenu',
            'component': '/newmenu/index.vue',
            'sort': 1,
            'meta': {'title': '新菜单'}
        }
        response = self.client.post('/api/authority/menus/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'NewMenu')

    def test_retrieve_menu(self):
        """测试获取单个菜单"""
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        response = self.client.get(f'/api/authority/menus/{menu.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Users')

    def test_update_menu(self):
        """测试更新菜单"""
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        data = {'name': 'UpdatedUsers'}
        response = self.client.put(f'/api/authority/menus/{menu.pk}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'UpdatedUsers')

    def test_delete_menu(self):
        """测试删除菜单"""
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        response = self.client.delete(f'/api/authority/menus/{menu.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Menu.objects.filter(pk=menu.pk).exists())

    def test_get_menu_tree(self):
        """测试获取菜单树"""
        parent = Menu.objects.create(path='/admin', name='Admin', sort=1)
        child = Menu.objects.create(path='/admin/users', name='Users', parent=parent, sort=1)
        response = self.client.get('/api/authority/menus/tree/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Admin')
        self.assertEqual(len(response.data['data'][0]['children']), 1)

    def test_menu_unauthorized(self):
        """测试未授权访问"""
        client = self.client.__class__()
        response = client.get('/api/authority/menus/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
