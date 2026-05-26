"""LBListener Serializer 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBListener
from backend.serializers.network import (
    LBListenerSerializer,
    LBListenerListSerializer,
    LBListenerCreateSerializer,
    LBListenerUpdateSerializer,
)


class LBListenerSerializerTest(TestCase):
    """LBListenerSerializer 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active'
        )
        self.listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80,
            name='TestListener',
            description='Test Listener'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = LBListenerSerializer(self.listener)
        data = serializer.data
        expected_fields = [
            'id', 'loadbalancer', 'loadbalancer_name', 'protocol',
            'port', 'name', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_field_values(self):
        """测试序列化器字段值正确"""
        serializer = LBListenerSerializer(self.listener)
        data = serializer.data
        self.assertEqual(data['loadbalancer'], self.lb.id)
        self.assertEqual(data['loadbalancer_name'], 'TestLB')
        self.assertEqual(data['protocol'], 'tcp')
        self.assertEqual(data['port'], 80)
        self.assertEqual(data['name'], 'TestListener')

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = LBListenerListSerializer(self.listener)
        data = serializer.data
        expected_fields = ['id', 'loadbalancer', 'loadbalancer_name', 'protocol', 'port', 'name']
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
            'protocol': 'http',
            'port': 8080,
            'name': 'NewListener',
            'description': 'New Listener'
        }
        serializer = LBListenerCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_protocol(self):
        """测试创建序列化器拒绝无效的协议"""
        data = {
            'loadbalancer': self.lb.id,
            'protocol': 'invalid_protocol',
            'port': 80
        }
        serializer = LBListenerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_missing_required_field(self):
        """测试创建序列化器拒绝缺少必需字段"""
        data = {
            'loadbalancer': self.lb.id,
            'protocol': 'tcp'
            # 缺少 port
        }
        serializer = LBListenerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'name': 'UpdatedListener',
            'protocol': 'https',
            'port': 8443
        }
        serializer = LBListenerUpdateSerializer(self.listener, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_partial(self):
        """测试更新序列化器部分更新"""
        data = {'port': 9999}
        serializer = LBListenerUpdateSerializer(self.listener, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        listener = serializer.save()
        self.assertEqual(listener.port, 9999)
        self.assertEqual(listener.protocol, 'tcp')  # 未更新的字段保持不变

    def test_update_serializer_invalid_protocol(self):
        """测试更新序列化器拒绝无效协议"""
        data = {'protocol': 'invalid'}
        serializer = LBListenerUpdateSerializer(self.listener, data=data, partial=True)
        self.assertFalse(serializer.is_valid())