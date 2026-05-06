import uuid

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.hashers import check_password

from backend.models import Users


class UsersModelTest(TestCase):
    """users 模型测试"""

    def test_create_user(self):
        """测试创建用户"""
        user = Users.objects.create(
            user='testuser',
            password='plainpass'
        )
        self.assertEqual(user.user, 'testuser')
        self.assertIsNotNone(user.uuid)
        self.assertIsInstance(user.uuid, uuid.UUID)

    def test_user_default_values(self):
        """测试用户默认值"""
        user = Users.objects.create(
            user='alice',
            password='pass123'
        )
        self.assertEqual(user.nickname, '系统用户')
        self.assertEqual(user.phone, '')
        self.assertEqual(user.email, '')
        self.assertEqual(user.enable, 1)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_user_uuid_unique(self):
        """测试UUID唯一性"""
        user1 = Users.objects.create(user='user1', password='pass')
        user2 = Users.objects.create(user='user2', password='pass')
        self.assertNotEqual(user1.uuid, user2.uuid)

    def test_user_unique_username(self):
        """测试用户名唯一"""
        Users.objects.create(user='uniqueuser', password='pass')
        with self.assertRaises(Exception):
            Users.objects.create(user='uniqueuser', password='pass2')

    def test_user_str(self):
        """测试用户字符串表示"""
        user = Users(user='john')
        self.assertEqual(str(user), 'john')

    def test_set_password(self):
        """测试密码加密"""
        user = Users.objects.create(user='passuser', password='oldpass')
        user.set_password('newpassword123')
        self.assertNotEqual(user.password, 'newpassword123')
        self.assertTrue(check_password('newpassword123', user.password))

    def test_is_active_enabled(self):
        """测试is_active启用状态"""
        user = Users.objects.create(user='active', password='pass', enable=1)
        self.assertTrue(user.is_active)

    def test_is_active_disabled(self):
        """测试is_active冻结状态"""
        user = Users.objects.create(user='frozen', password='pass', enable=2)
        self.assertFalse(user.is_active)

    def test_user_meta_verbose_name(self):
        """测试Meta配置"""
        self.assertEqual(Users._meta.verbose_name, '用户')
        self.assertEqual(Users._meta.verbose_name_plural, '用户')
        self.assertEqual(Users._meta.db_table, 'users')

    def test_user_with_email(self):
        """测试用户邮箱字段"""
        user = Users.objects.create(
            user='emailuser',
            password='pass',
            email='test@example.com'
        )
        self.assertEqual(user.email, 'test@example.com')

    def test_user_with_phone(self):
        """测试用户手机字段"""
        user = Users.objects.create(
            user='phoneuser',
            password='pass',
            phone='13800138000'
        )
        self.assertEqual(user.phone, '13800138000')

    def test_user_created_at_auto(self):
        """测试创建时间自动生成"""
        before = timezone.now()
        user = Users.objects.create(user='timeuser', password='pass')
        after = timezone.now()
        self.assertLessEqual(user.created_at, after)
        self.assertGreaterEqual(user.created_at, before)

    def test_user_updated_at_auto(self):
        """测试更新时间自动更新"""
        user = Users.objects.create(user='updateuser', password='pass')
        original_updated = user.updated_at
        user.nickname = '新昵称'
        user.save()
        user.refresh_from_db()
        self.assertGreater(user.updated_at, original_updated)


from backend.serializers import UserSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from io import BytesIO


class UserSerializerTest(TestCase):
    """UserSerializer 测试"""

    def test_serialize_user(self):
        """测试用户序列化"""
        user = Users.objects.create(
            user='testuser',
            password='testpass123'
        )
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['user'], 'testuser')
        self.assertEqual(data['nickname'], '系统用户')
        self.assertIn('uuid', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        # password should not be in output
        self.assertNotIn('password', data)

    def test_serialize_user_with_all_fields(self):
        """测试包含所有字段的用户序列化"""
        user = Users.objects.create(
            user='fulluser',
            password='pass123',
            nickname='完整用户',
            phone='13800138000',
            email='test@example.com',
            enable=1
        )
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['user'], 'fulluser')
        self.assertEqual(data['nickname'], '完整用户')
        self.assertEqual(data['phone'], '13800138000')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['enable'], 1)

    def test_deserialize_create_user(self):
        """测试创建用户反序列化"""
        data = {
            'user': 'newuser',
            'password': 'newpass123',
            'nickname': '新用户',
            'phone': '13900001111',
            'email': 'new@example.com',
            'enable': 1
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.user, 'newuser')
        self.assertEqual(user.nickname, '新用户')
        self.assertEqual(user.phone, '13900001111')
        self.assertEqual(user.email, 'new@example.com')
        self.assertNotEqual(user.password, 'newpass123')

    def test_deserialize_create_without_password(self):
        """测试不带密码创建用户"""
        data = {
            'user': 'nopassuser',
            'nickname': '无密码用户'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.user, 'nopassuser')

    def test_update_user(self):
        """测试更新用户"""
        user = Users.objects.create(
            user='updateuser',
            password='oldpass',
            nickname='旧昵称'
        )
        data = {
            'user': 'updateuser',
            'nickname': '新昵称',
            'phone': '13812345678'
        }
        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.update(user, data)
        self.assertEqual(updated_user.nickname, '新昵称')
        self.assertEqual(updated_user.phone, '13812345678')

    def test_update_password(self):
        """测试更新密码"""
        user = Users.objects.create(
            user='passuser',
            password='oldpass123'
        )
        data = {
            'user': 'passuser',
            'password': 'newpass456'
        }
        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.update(user, data)
        self.assertTrue(check_password('newpass456', updated_user.password))

    def test_read_only_fields(self):
        """测试只读字段不可修改"""
        user = Users.objects.create(
            user='readonlyuser',
            password='pass'
        )
        original_uuid = str(user.uuid)
        original_created_at = user.created_at
        data = {
            'user': 'readonlyuser',
            'uuid': '00000000-0000-0000-0000-000000000000',
            'created_at': '2020-01-01T00:00:00Z'
        }
        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(str(updated_user.uuid), original_uuid)

    def test_enable_field_values(self):
        """测试enable字段的序列化和反序列化"""
        user1 = Users.objects.create(user='enabled', password='pass', enable=1)
        user2 = Users.objects.create(user='disabled', password='pass', enable=2)
        serializer1 = UserSerializer(user1)
        serializer2 = UserSerializer(user2)
        self.assertEqual(serializer1.data['enable'], 1)
        self.assertEqual(serializer2.data['enable'], 2)


from backend.serializers import UserCreateSerializer, ChangePasswordSerializer


class UserCreateSerializerTest(TestCase):
    """UserCreateSerializer 测试"""

    def test_create_user_success(self):
        """测试成功创建用户"""
        data = {
            'user': 'newuser1',
            'password': 'pass123',
            'nickname': '新用户',
            'phone': '13800138000',
            'email': 'test@example.com'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.user, 'newuser1')
        self.assertEqual(user.nickname, '新用户')
        self.assertEqual(user.phone, '13800138000')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(check_password('pass123', user.password))

    def test_create_user_without_optional_fields(self):
        """测试仅使用必填字段创建用户"""
        data = {
            'user': 'minimaluser',
            'password': 'minpass'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.user, 'minimaluser')
        self.assertEqual(user.nickname, '系统用户')

    def test_create_user_password_too_short(self):
        """测试密码过短"""
        data = {
            'user': 'shortpass',
            'password': '12345'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user_missing_password(self):
        """测试缺少密码"""
        data = {
            'user': 'nopass'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user_duplicate_username(self):
        """测试重复用户名"""
        Users.objects.create(user='existing', password='pass')
        data = {
            'user': 'existing',
            'password': 'newpass'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ChangePasswordSerializerTest(TestCase):
    """ChangePasswordSerializer 测试"""

    def test_valid_data(self):
        """测试有效数据"""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass456'
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_old_password(self):
        """测试缺少旧密码"""
        data = {
            'new_password': 'newpass456'
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)

    def test_missing_new_password(self):
        """测试缺少新密码"""
        data = {
            'old_password': 'oldpass123'
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)

    def test_new_password_too_short(self):
        """测试新密码过短"""
        data = {
            'old_password': 'oldpass123',
            'new_password': '12345'
        }
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)


from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


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
        self.admin_user = Users.objects.create(
            user='admin',
            password='adminpass123',
            nickname='管理员',
            enable=1
        )
        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_client = self.client.__class__()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')

    def test_me_get_success(self):
        """测试GET /me/ 获取当前用户信息"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], 'testuser')
        self.assertEqual(response.data['nickname'], '测试用户')
        self.assertIn('uuid', response.data)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], '新昵称')
        self.assertEqual(response.data['phone'], '13900001111')

    def test_me_put_partial_update(self):
        """测试PATCH /me/ 部分更新"""
        data = {'nickname': '部分更新'}
        response = self.client.put('/api/users/me/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], '部分更新')

    def test_me_put_invalid_data(self):
        """测试PUT /me/ 无效数据应返回400"""
        data = {'email': 'not-an-email'}
        response = self.client.put('/api/users/me/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_password_success(self):
        """测试管理员重置用户密码"""
        data = {'new_password': 'newresetpass123'}
        response = self.admin_client.put(f'/api/users/{self.user.pk}/password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '密码重置成功')
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '密码修改成功')

    def test_change_my_password_wrong_old_password(self):
        """测试修改密码旧密码错误应返回400"""
        data = {'old_password': 'wrongoldpass', 'new_password': 'newpass123'}
        response = self.client.put('/api/users/me/password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_change_my_password_without_auth(self):
        """测试修改密码无认证应返回401"""
        client = self.client.__class__()
        data = {'old_password': 'oldpass', 'new_password': 'newpass123'}
        response = client.put('/api/users/me/password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_role_not_implemented(self):
        """测试设置角色返回501未实现"""
        data = {'role': 'admin'}
        response = self.admin_client.put(f'/api/users/{self.user.pk}/role/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_list_users(self):
        """测试列出用户列表"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """测试创建新用户"""
        data = {
            'user': 'newcreateuser',
            'password': 'newcreatepass123',
            'nickname': '新创建用户'
        }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], 'newcreateuser')

    def test_retrieve_user(self):
        """测试获取单个用户"""
        response = self.client.get(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], 'testuser')

    def test_destroy_user(self):
        """测试删除用户"""
        response = self.client.delete(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Users.objects.filter(pk=self.user.pk).exists())


from backend.authentication import redis_client


class MockRedisTest(TestCase):
    """MockRedis 测试"""

    def setUp(self):
        """重置MockRedis存储"""
        redis_client._store.clear()

    def test_set_and_get(self):
        """测试基本设置和获取"""
        redis_client.set('key1', 'value1')
        self.assertEqual(redis_client.get('key1'), 'value1')

    def test_set_with_expiry(self):
        """测试带过期时间的设置"""
        import time
        redis_client.set('key2', 'value2', ex=2)
        self.assertEqual(redis_client.get('key2'), 'value2')
        # TTL should be positive
        ttl = redis_client.ttl('key2')
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 2)

    def test_get_expired_key(self):
        """测试获取已过期的键"""
        import time
        redis_client.set('key3', 'value3', ex=1)
        time.sleep(1.1)
        self.assertIsNone(redis_client.get('key3'))

    def test_ttl_nonexistent_key(self):
        """测试不存在键的TTL"""
        self.assertEqual(redis_client.ttl('nonexistent'), -2)

    def test_ttl_permanent_key(self):
        """测试永久键的TTL"""
        redis_client.set('key4', 'value4')
        self.assertEqual(redis_client.ttl('key4'), -1)

    def test_delete(self):
        """测试删除键"""
        redis_client.set('key5', 'value5')
        self.assertTrue(redis_client.delete('key5'))
        self.assertIsNone(redis_client.get('key5'))

    def test_exists(self):
        """测试exists方法"""
        redis_client.set('key6', 'value6')
        self.assertTrue(redis_client.exists('key6'))
        self.assertFalse(redis_client.exists('nonexistent'))

    def test_exists_after_expiry(self):
        """测试过期后exists返回False"""
        import time
        redis_client.set('key7', 'value7', ex=1)
        time.sleep(1.1)
        self.assertFalse(redis_client.exists('key7'))

    def test_expire_method(self):
        """测试expire方法设置过期时间"""
        import time
        redis_client.set('key8', 'value8')
        redis_client.expire('key8', 3)
        ttl = redis_client.ttl('key8')
        self.assertGreater(ttl, 0)
        self.assertLessEqual(ttl, 3)

    def test_expire_nonexistent_key(self):
        """测试对不存在键设置过期返回False"""
        self.assertFalse(redis_client.expire('nonexistent', 10))

    def test_set_overwrites_existing(self):
        """测试设置已存在的键会覆盖"""
        redis_client.set('key9', 'old')
        redis_client.set('key9', 'new')
        self.assertEqual(redis_client.get('key9'), 'new')

    def test_set_updates_expiry(self):
        """测试重新设置会更新过期时间"""
        import time
        redis_client.set('key10', 'value10', ex=10)
        redis_client.set('key10', 'value10', ex=1)
        ttl = redis_client.ttl('key10')
        self.assertLessEqual(ttl, 1)


# ============ Authority 模块模型和序列化器测试 ============

from backend.models import Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority
from backend.authority_serializers import (
    AuthoritySerializer, AuthorityCreateSerializer,
    MenuSerializer, MenuTreeSerializer, MenuButtonSerializer,
    UserAuthoritySerializer, SetUserRoleSerializer
)


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
