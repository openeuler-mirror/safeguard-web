from django.test import TestCase

from backend.serializers.user import ChangePasswordSerializer


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
