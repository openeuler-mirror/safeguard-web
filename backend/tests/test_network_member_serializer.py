"""LBMember Serializer 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBMember
from backend.serializers.network import (
    LBMemberSerializer,
    LBMemberListSerializer,
    LBMemberCreateSerializer,
    LBMemberUpdateSerializer,
)


class LBMemberSerializerTest(TestCase):
    """LBMemberSerializer 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active'
        )
        self.pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='TestPool',
            protocol='tcp'
        )
        self.member = LBMember.objects.create(
            pool=self.pool,
            address='192.168.1.10',
            port=8080,
            weight=1,
            is_enabled=True,
            description='Test Member'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = LBMemberSerializer(self.member)
        data = serializer.data
        expected_fields = [
            'id', 'pool', 'pool_name', 'address', 'port',
            'weight', 'is_enabled', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_field_values(self):
        """测试序列化器字段值正确"""
        serializer = LBMemberSerializer(self.member)
        data = serializer.data
        self.assertEqual(data['pool'], self.pool.id)
        self.assertEqual(data['pool_name'], 'TestPool')
        self.assertEqual(data['address'], '192.168.1.10')
        self.assertEqual(data['port'], 8080)
        self.assertEqual(data['weight'], 1)
        self.assertTrue(data['is_enabled'])

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = LBMemberListSerializer(self.member)
        data = serializer.data
        expected_fields = ['id', 'pool', 'pool_name', 'address', 'port', 'weight', 'is_enabled']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('description', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'pool': self.pool.id,
            'address': '192.168.1.20',
            'port': 9090,
            'weight': 2,
            'is_enabled': True,
            'description': 'New Member'
        }
        serializer = LBMemberCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_with_defaults(self):
        """测试创建序列化器使用默认值"""
        data = {
            'pool': self.pool.id,
            'address': '192.168.1.30',
            'port': 8080
        }
        serializer = LBMemberCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_ip(self):
        """测试创建序列化器拒绝无效的IP地址"""
        data = {
            'pool': self.pool.id,
            'address': 'not-an-ip',
            'port': 8080
        }
        serializer = LBMemberCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_missing_required_field(self):
        """测试创建序列化器拒绝缺少必需字段"""
        data = {
            'pool': self.pool.id,
            'address': '192.168.1.40'
            # 缺少 port
        }
        serializer = LBMemberCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'address': '192.168.1.99',
            'weight': 5,
            'is_enabled': False
        }
        serializer = LBMemberUpdateSerializer(self.member, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_partial(self):
        """测试更新序列化器部分更新"""
        data = {'weight': 10}
        serializer = LBMemberUpdateSerializer(self.member, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        member = serializer.save()
        self.assertEqual(member.weight, 10)
        self.assertEqual(member.address, '192.168.1.10')  # 未更新的字段保持不变

    def test_update_serializer_invalid_ip(self):
        """测试更新序列化器拒绝无效IP"""
        data = {'address': 'invalid-ip'}
        serializer = LBMemberUpdateSerializer(self.member, data=data, partial=True)
        self.assertFalse(serializer.is_valid())