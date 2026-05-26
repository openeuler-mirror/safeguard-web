"""LBHealthMonitor Serializer 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBHealthMonitor
from backend.serializers.network import (
    LBHealthMonitorSerializer,
    LBHealthMonitorListSerializer,
    LBHealthMonitorCreateSerializer,
    LBHealthMonitorUpdateSerializer,
)


class LBHealthMonitorSerializerTest(TestCase):
    """LBHealthMonitorSerializer 测试"""

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
        self.monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3,
            description='Test Health Monitor'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = LBHealthMonitorSerializer(self.monitor)
        data = serializer.data
        expected_fields = [
            'id', 'pool', 'pool_name', 'monitor_type',
            'interval', 'timeout', 'retry', 'description',
            'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_field_values(self):
        """测试序列化器字段值正确"""
        serializer = LBHealthMonitorSerializer(self.monitor)
        data = serializer.data
        self.assertEqual(data['pool'], self.pool.id)
        self.assertEqual(data['pool_name'], 'TestPool')
        self.assertEqual(data['monitor_type'], 'tcp')
        self.assertEqual(data['interval'], 5)
        self.assertEqual(data['timeout'], 3)
        self.assertEqual(data['retry'], 3)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = LBHealthMonitorListSerializer(self.monitor)
        data = serializer.data
        expected_fields = ['id', 'pool', 'pool_name', 'monitor_type', 'interval', 'timeout', 'retry']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('description', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        new_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='NewPool',
            protocol='http'
        )
        data = {
            'pool': new_pool.id,
            'monitor_type': 'http',
            'interval': 10,
            'timeout': 5,
            'retry': 3,
            'description': 'New Monitor'
        }
        serializer = LBHealthMonitorCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_with_defaults(self):
        """测试创建序列化器使用默认值"""
        new_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='DefaultPool',
            protocol='http'
        )
        data = {
            'pool': new_pool.id,
            'monitor_type': 'ping'
        }
        serializer = LBHealthMonitorCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_type(self):
        """测试创建序列化器拒绝无效的检查类型"""
        data = {
            'pool': self.pool.id,
            'monitor_type': 'invalid_type'
        }
        serializer = LBHealthMonitorCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_missing_required_field(self):
        """测试创建序列化器拒绝缺少必需字段"""
        data = {
            'pool': self.pool.id,
            'interval': 10
            # 缺少 monitor_type
        }
        serializer = LBHealthMonitorCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'monitor_type': 'http',
            'interval': 20,
            'timeout': 10,
            'retry': 5,
            'description': 'Updated Monitor'
        }
        serializer = LBHealthMonitorUpdateSerializer(self.monitor, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_partial(self):
        """测试更新序列化器部分更新"""
        data = {'interval': 15}
        serializer = LBHealthMonitorUpdateSerializer(self.monitor, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        monitor = serializer.save()
        self.assertEqual(monitor.interval, 15)
        self.assertEqual(monitor.monitor_type, 'tcp')  # 未更新的字段保持不变

    def test_update_serializer_invalid_type(self):
        """测试更新序列化器拒绝无效类型"""
        data = {'monitor_type': 'invalid'}
        serializer = LBHealthMonitorUpdateSerializer(self.monitor, data=data, partial=True)
        self.assertFalse(serializer.is_valid())