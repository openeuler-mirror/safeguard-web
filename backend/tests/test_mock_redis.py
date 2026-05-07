from django.test import TestCase

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
from backend.serializers.authority import (
    AuthoritySerializer, AuthorityCreateSerializer,
    MenuSerializer, MenuTreeSerializer, MenuButtonSerializer,
    UserAuthoritySerializer, SetUserRoleSerializer
)


