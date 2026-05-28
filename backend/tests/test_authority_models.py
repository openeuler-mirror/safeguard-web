from django.test import TestCase

from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority, Users


class AuthorityModelTest(TestCase):
    """Authority 模型测试"""

    def test_create_authority(self):
        """测试创建角色"""
        auth = Authority.objects.create(
            authority_id=1,
            authority_name='管理员'
        )
        self.assertEqual(auth.authority_id, 1)
        self.assertEqual(auth.authority_name, '管理员')
        self.assertEqual(auth.default_router, 'dashboard')

    def test_authority_with_parent(self):
        """测试角色层级关系"""
        parent = Authority.objects.create(authority_id=1, authority_name='超级管理员')
        child = Authority.objects.create(
            authority_id=2,
            authority_name='普通管理员',
            parent=parent
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_authority_with_data_authority(self):
        """测试数据权限范围"""
        scope = Authority.objects.create(authority_id=1, authority_name='A级数据')
        auth = Authority.objects.create(
            authority_id=2,
            authority_name='B级数据',
            data_authority=scope
        )
        self.assertEqual(auth.data_authority, scope)
        self.assertIn(auth, scope.data_scope.all())

    def test_authority_unique_id(self):
        """测试角色ID唯一性"""
        Authority.objects.create(authority_id=1, authority_name='角色1')
        with self.assertRaises(Exception):
            Authority.objects.create(authority_id=1, authority_name='角色2')

    def test_authority_str(self):
        """测试角色字符串表示"""
        auth = Authority(authority_name='测试角色')
        self.assertEqual(str(auth), '测试角色')

    def test_authority_default_router(self):
        """测试默认路由默认值"""
        auth = Authority.objects.create(authority_id=1, authority_name='新角色')
        self.assertEqual(auth.default_router, 'dashboard')


class MenuModelTest(TestCase):
    """Menu 模型测试"""

    def test_create_menu(self):
        """测试创建菜单"""
        menu = Menu.objects.create(
            path='/users',
            name='UserList',
            component='/users/index.vue',
            sort=1
        )
        self.assertEqual(menu.path, '/users')
        self.assertEqual(menu.name, 'UserList')
        self.assertEqual(menu.sort, 1)

    def test_menu_with_parent(self):
        """测试菜单层级关系"""
        parent = Menu.objects.create(path='/admin', name='Admin', sort=1)
        child = Menu.objects.create(
            path='/admin/users',
            name='UserManagement',
            parent=parent,
            sort=1
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_menu_with_meta(self):
        """测试菜单元数据"""
        menu = Menu.objects.create(
            path='/dashboard',
            name='Dashboard',
            meta={'title': '仪表盘', 'icon': 'dashboard'}
        )
        self.assertEqual(menu.meta['title'], '仪表盘')
        self.assertEqual(menu.meta['icon'], 'dashboard')

    def test_menu_ordering(self):
        """测试菜单排序"""
        Menu.objects.create(path='/b', name='B', sort=2)
        Menu.objects.create(path='/a', name='A', sort=1)
        Menu.objects.create(path='/c', name='C', sort=3)
        menus = list(Menu.objects.all())
        self.assertEqual(menus[0].name, 'A')
        self.assertEqual(menus[1].name, 'B')
        self.assertEqual(menus[2].name, 'C')


class MenuButtonModelTest(TestCase):
    """MenuButton 模型测试"""

    def setUp(self):
        self.menu = Menu.objects.create(path='/users', name='Users', sort=1)

    def test_create_button(self):
        """测试创建按钮"""
        btn = MenuButton.objects.create(
            menu=self.menu,
            name='add',
            desc='添加用户'
        )
        self.assertEqual(btn.name, 'add')
        self.assertEqual(btn.desc, '添加用户')
        self.assertEqual(btn.menu, self.menu)

    def test_button_str(self):
        """测试按钮字符串表示"""
        btn = MenuButton(menu=self.menu, name='edit')
        self.assertEqual(str(btn), 'Users - edit')

    def test_menu_buttons_relation(self):
        """测试菜单与按钮的关系"""
        btn1 = MenuButton.objects.create(menu=self.menu, name='add')
        btn2 = MenuButton.objects.create(menu=self.menu, name='edit')
        self.assertEqual(self.menu.buttons.count(), 2)
        self.assertIn(btn1, self.menu.buttons.all())
        self.assertIn(btn2, self.menu.buttons.all())


class AuthorityMenuModelTest(TestCase):
    """AuthorityMenu 模型测试"""

    def setUp(self):
        self.auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        self.menu = Menu.objects.create(path='/admin', name='Admin', sort=1)

    def test_create_authority_menu(self):
        """测试创建角色菜单关联"""
        am = AuthorityMenu.objects.create(authority=self.auth, menu=self.menu)
        self.assertEqual(am.authority, self.auth)
        self.assertEqual(am.menu, self.menu)

    def test_authority_menus_relation(self):
        """测试角色与菜单的关系"""
        menu2 = Menu.objects.create(path='/users', name='Users', sort=2)
        AuthorityMenu.objects.create(authority=self.auth, menu=self.menu)
        AuthorityMenu.objects.create(authority=self.auth, menu=menu2)
        self.assertEqual(self.auth.authoritymenu_set.count(), 2)

    def test_unique_together_constraint(self):
        """测试唯一约束"""
        AuthorityMenu.objects.create(authority=self.auth, menu=self.menu)
        with self.assertRaises(Exception):
            AuthorityMenu.objects.create(authority=self.auth, menu=self.menu)


class AuthorityButtonModelTest(TestCase):
    """AuthorityButton 模型测试"""

    def setUp(self):
        self.auth = Authority.objects.create(authority_id=1, authority_name='管理员')
        self.menu = Menu.objects.create(path='/admin', name='Admin', sort=1)
        self.btn = MenuButton.objects.create(menu=self.menu, name='add')

    def test_create_authority_button(self):
        """测试创建角色按钮关联"""
        ab = AuthorityButton.objects.create(
            authority=self.auth,
            menu=self.menu,
            button=self.btn
        )
        self.assertEqual(ab.authority, self.auth)
        self.assertEqual(ab.menu, self.menu)
        self.assertEqual(ab.button, self.btn)


class UserAuthorityModelTest(TestCase):
    """UserAuthority 模型测试"""

    def setUp(self):
        self.user = Users.objects.create(user='testuser', password='pass')
        self.auth = Authority.objects.create(authority_id=1, authority_name='管理员')

    def test_create_user_authority(self):
        """测试创建用户角色关联"""
        ua = UserAuthority.objects.create(user=self.user, authority=self.auth)
        self.assertEqual(ua.user, self.user)
        self.assertEqual(ua.authority, self.auth)

    def test_user_authorities_relation(self):
        """测试用户与角色的关系"""
        auth2 = Authority.objects.create(authority_id=2, authority_name='普通用户')
        UserAuthority.objects.create(user=self.user, authority=self.auth)
        UserAuthority.objects.create(user=self.user, authority=auth2)
        self.assertEqual(self.user.userauthority_set.count(), 2)

    def test_unique_together_constraint(self):
        """测试用户角色唯一约束"""
        UserAuthority.objects.create(user=self.user, authority=self.auth)
        with self.assertRaises(Exception):
            UserAuthority.objects.create(user=self.user, authority=self.auth)


