"""LoadBalancer Serializer 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer
from backend.serializers.network import (
    LoadBalancerSerializer,
    LoadBalancerListSerializer,
    LoadBalancerCreateSerializer,
    LoadBalancerUpdateSerializer,
)


class LoadBalancerSerializerTest(TestCase):
    """LoadBalancerSerializer 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active',
            description='Test LoadBalancer'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = LoadBalancerSerializer(self.lb)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'vip_address', 'port', 'algorithm',
            'status', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_field_values(self):
        """测试序列化器字段值正确"""
        serializer = LoadBalancerSerializer(self.lb)
        data = serializer.data
        self.assertEqual(data['name'], 'TestLB')
        self.assertEqual(data['vip_address'], '192.168.1.100')
        self.assertEqual(data['port'], 80)
        self.assertEqual(data['algorithm'], 'round_robin')
        self.assertEqual(data['status'], 'active')

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = LoadBalancerListSerializer(self.lb)
        data = serializer.data
        expected_fields = ['id', 'name', 'vip_address', 'port', 'algorithm', 'status']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('description', data)
        self.assertNotIn('created_at', data)
        self.assertNotIn('updated_at', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'name': 'NewLB',
            'vip_address': '192.168.1.200',
            'port': 8080,
            'algorithm': 'least_conn',
            'status': 'active',
            'description': 'New LoadBalancer'
        }
        serializer = LoadBalancerCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_valid_data_with_defaults(self):
        """测试创建序列化器有效数据（使用默认值）"""
        data = {
            'name': 'NewLB',
            'vip_address': '192.168.1.200',
        }
        serializer = LoadBalancerCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_algorithm(self):
        """测试创建序列化器拒绝无效的负载算法"""
        data = {
            'name': 'InvalidLB',
            'vip_address': '192.168.1.200',
            'algorithm': 'invalid_algorithm'
        }
        serializer = LoadBalancerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_invalid_ip(self):
        """测试创建序列化器拒绝无效的IP地址"""
        data = {
            'name': 'InvalidLB',
            'vip_address': 'not-an-ip',
            'port': 80
        }
        serializer = LoadBalancerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_serializer_invalid_port(self):
        """测试创建序列化器拒绝无效端口"""
        data = {
            'name': 'InvalidLB',
            'vip_address': '192.168.1.200',
            'port': 99999  # 无效端口
        }
        serializer = LoadBalancerCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'name': 'UpdatedLB',
            'algorithm': 'source',
            'description': 'Updated description'
        }
        serializer = LoadBalancerUpdateSerializer(self.lb, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_partial(self):
        """测试更新序列化器部分更新"""
        data = {'status': 'inactive'}
        serializer = LoadBalancerUpdateSerializer(self.lb, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        lb = serializer.save()
        self.assertEqual(lb.status, 'inactive')
        self.assertEqual(lb.name, 'TestLB')  # 未更新的字段保持不变