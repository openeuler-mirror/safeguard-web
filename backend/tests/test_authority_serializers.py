from django.test import TestCase

from backend.models import Authority, Menu, MenuButton, AuthorityMenu, UserAuthority, Users
from backend.serializers.authority import (
    AuthoritySerializer, AuthorityCreateSerializer,
    MenuSerializer, MenuTreeSerializer, MenuButtonSerializer,
    UserAuthoritySerializer, SetUserRoleSerializer
)


class AuthoritySerializerTest(TestCase):
    """AuthoritySerializer 测试"""

    def test_serialize_authority(self):
        """测试角色序列化"""
        parent = Authority.objects.create(authority_id=1, authority_name='超级管理员')
        auth = Authority.objects.create(
            authority_id=2,
            authority_name='普通管理员',
            parent=parent,
            default_router='/home'
        )
        serializer = AuthoritySerializer(auth)
        data = serializer.data
        self.assertEqual(data['authority_id'], 2)
        self.assertEqual(data['authority_name'], '普通管理员')
        self.assertEqual(data['parent'], parent.id)
        self.assertEqual(data['parent_name'], '超级管理员')
        self.assertEqual(data['default_router'], '/home')

    def test_serialize_with_data_authority(self):
        """测试带数据权限的角色序列化"""
        scope = Authority.objects.create(authority_id=1, authority_name='A级数据')
        auth = Authority.objects.create(
            authority_id=2,
            authority_name='B级数据',
            data_authority=scope
        )
        serializer = AuthoritySerializer(auth)
        data = serializer.data
        self.assertEqual(data['data_authority'], scope.id)
        self.assertEqual(data['data_authority_name'], 'A级数据')


class AuthorityCreateSerializerTest(TestCase):
    """AuthorityCreateSerializer 测试"""

    def test_create_authority(self):
        """测试创建角色"""
        data = {
            'authority_id': 1,
            'authority_name': '新角色',
            'default_router': '/dashboard'
        }
        serializer = AuthorityCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        auth = serializer.save()
        self.assertEqual(auth.authority_id, 1)
        self.assertEqual(auth.authority_name, '新角色')

    def test_create_with_parent(self):
        """测试创建带父角色的角色"""
        parent = Authority.objects.create(authority_id=1, authority_name='父角色')
        data = {
            'authority_id': 2,
            'authority_name': '子角色',
            'parent': parent.id
        }
        serializer = AuthorityCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        auth = serializer.save()
        self.assertEqual(auth.parent, parent)


class MenuSerializerTest(TestCase):
    """MenuSerializer 测试"""

    def test_serialize_menu(self):
        """测试菜单序列化"""
        menu = Menu.objects.create(
            path='/users',
            name='UserList',
            component='/users/index.vue',
            sort=1,
            meta={'title': '用户列表'}
        )
        serializer = MenuSerializer(menu)
        data = serializer.data
        self.assertEqual(data['path'], '/users')
        self.assertEqual(data['name'], 'UserList')
        self.assertEqual(data['component'], '/users/index.vue')
        self.assertEqual(data['sort'], 1)
        self.assertEqual(data['meta']['title'], '用户列表')

    def test_serialize_menu_with_buttons(self):
        """测试菜单序列化包含按钮"""
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        MenuButton.objects.create(menu=menu, name='add', desc='添加')
        MenuButton.objects.create(menu=menu, name='edit', desc='编辑')
        serializer = MenuSerializer(menu)
        data = serializer.data
        self.assertEqual(len(data['buttons']), 2)


class MenuTreeSerializerTest(TestCase):
    """MenuTreeSerializer 测试"""

    def test_serialize_menu_tree(self):
        """测试菜单树序列化"""
        parent = Menu.objects.create(path='/admin', name='Admin', sort=1)
        child = Menu.objects.create(path='/admin/users', name='Users', parent=parent, sort=1)
        grandchild = Menu.objects.create(path='/admin/users/list', name='UserList', parent=child, sort=1)

        serializer = MenuTreeSerializer(parent)
        data = serializer.data

        self.assertEqual(data['name'], 'Admin')
        self.assertEqual(len(data['children']), 1)
        self.assertEqual(data['children'][0]['name'], 'Users')
        self.assertEqual(len(data['children'][0]['children']), 1)
        self.assertEqual(data['children'][0]['children'][0]['name'], 'UserList')


class MenuButtonSerializerTest(TestCase):
    """MenuButtonSerializer 测试"""

    def test_serialize_button(self):
        """测试按钮序列化"""
        menu = Menu.objects.create(path='/users', name='Users', sort=1)
        btn = MenuButton.objects.create(menu=menu, name='add', desc='添加用户')
        serializer = MenuButtonSerializer(btn)
        data = serializer.data
        self.assertEqual(data['name'], 'add')
        self.assertEqual(data['desc'], '添加用户')
        self.assertEqual(data['menu'], menu.id)


class UserAuthoritySerializerTest(TestCase):
    """UserAuthoritySerializer 测试"""

    def test_serialize_user_authority(self):
        """测试用户角色关联序列化"""
        user = Users.objects.create(user='testuser', password='pass')
        auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        ua = UserAuthority.objects.create(user=user, authority=auth)
        serializer = UserAuthoritySerializer(ua)
        data = serializer.data
        self.assertEqual(data['user'], user.id)
        self.assertEqual(data['user_username'], 'testuser')
        self.assertEqual(data['authority'], auth.id)
        self.assertEqual(data['authority_name'], '管理员')


