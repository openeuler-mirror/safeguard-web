"""LBPool Serializer 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool
from backend.serializers.network import (
    LBPoolSerializer,
    LBPoolListSerializer,
    LBPoolCreateSerializer,
    LBPoolUpdateSerializer,
)


class LBPoolSerializerTest(TestCase):
    """LBPoolSerializer 测试"""

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
            protocol='tcp',
            description='Test Pool'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = LBPoolSerializer(self.pool)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'loadbalancer', 'loadbalancer_name',
            'protocol', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_field_values(self):
        """测试序列化器字段值正确"""
        serializer = LBPoolSerializer(self.pool)
        data = serializer.data
        self.assertEqual(data['loadbalancer'], self.lb.id)
        self.assertEqual(data['loadbalancer_name'], 'TestLB')
        self.assertEqual(data['name'], 'TestPool')
        self.assertEqual(data['protocol'], 'tcp')

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = LBPoolListSerializer(self.pool)
        data = serializer.data
        expected_fields = ['id', 'name', 'loadbalancer', 'loadbalancer_name', 'protocol']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('description', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'loadbalancer': self.lb.id,
            'name': 'NewPool',
            'protocol': 'http',
            'description': 'New Pool'
        }
        serializer = LBPoolCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_protocol(self):
        """测试创建序列化器拒绝无效的协议"""
        data = {
            'loadbalancer': self.lb.id,
            'name': 'InvalidPool',
            'protocol': 'invalid_protocol'
        }
        serializer = LBPoolCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_missing_required_field(self):
        """测试创建序列化器拒绝缺少必需字段"""
        data = {
            'loadbalancer': self.lb.id,
            'protocol': 'tcp'
            # 缺少 name
        }
        serializer = LBPoolCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'name': 'UpdatedPool',
            'protocol': 'https',
            'description': 'Updated description'
        }
        serializer = LBPoolUpdateSerializer(self.pool, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_partial(self):
        """测试更新序列化器部分更新"""
        data = {'description': 'Only description updated'}
        serializer = LBPoolUpdateSerializer(self.pool, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        pool = serializer.save()
        self.assertEqual(pool.description, 'Only description updated')
        self.assertEqual(pool.name, 'TestPool')  # 未更新的字段保持不变