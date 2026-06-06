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

    def test_user_avatar_default(self):
        """测试头像默认值"""
        user = Users.objects.create(user='avataruser', password='pass')
        self.assertEqual(user.avatar, '')

    def test_user_theme_default(self):
        """测试主题默认值"""
        user = Users.objects.create(user='themeuser', password='pass')
        self.assertEqual(user.theme, 'light')
