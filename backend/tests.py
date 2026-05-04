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
        updated_user = serializer.save()
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
        updated_user = serializer.save()
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
