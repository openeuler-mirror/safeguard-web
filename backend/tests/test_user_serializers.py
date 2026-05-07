from django.test import TestCase
from django.contrib.auth.hashers import check_password

from backend.models import Users
from backend.serializers import UserSerializer


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
