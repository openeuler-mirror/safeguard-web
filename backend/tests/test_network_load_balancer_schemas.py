"""LoadBalancer Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.network.load_balancer import (
    LoadBalancerBase,
    LoadBalancerCreateRequest,
    LoadBalancerUpdateRequest,
    LoadBalancerResponse,
)


class LoadBalancerBaseSchemaTest(TestCase):
    """LoadBalancer 基础模型测试"""

    def test_load_balancer_base_valid(self):
        """测试有效的负载均衡器基础模型"""
        data = {
            'name': 'TestLB',
            'vip_address': '192.168.1.100',
            'port': 80,
            'algorithm': 'round_robin',
            'status': 'active',
            'description': '测试负载均衡器'
        }
        schema = LoadBalancerBase(**data)
        self.assertEqual(schema.name, 'TestLB')
        self.assertEqual(schema.vip_address, '192.168.1.100')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.algorithm, 'round_robin')
        self.assertEqual(schema.status, 'active')
        self.assertEqual(schema.description, '测试负载均衡器')

    def test_load_balancer_base_minimal(self):
        """测试最小负载均衡器数据"""
        schema = LoadBalancerBase(name='MinimalLB', vip_address='192.168.1.1')
        self.assertEqual(schema.name, 'MinimalLB')
        self.assertEqual(schema.vip_address, '192.168.1.1')
        self.assertEqual(schema.port, 80)  # 默认端口
        self.assertEqual(schema.algorithm, 'round_robin')  # 默认算法
        self.assertEqual(schema.status, 'active')  # 默认状态
        self.assertEqual(schema.description, '')

    def test_load_balancer_base_default_values(self):
        """测试负载均衡器默认值"""
        schema = LoadBalancerBase(name='DefaultLB', vip_address='10.0.0.1')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.algorithm, 'round_robin')
        self.assertEqual(schema.status, 'active')
        self.assertEqual(schema.description, '')

    def test_load_balancer_name_required(self):
        """测试名称为必填"""
        with self.assertRaises(Exception):
            LoadBalancerBase(vip_address='192.168.1.1')

    def test_load_balancer_vip_address_required(self):
        """测试VIP地址为必填"""
        with self.assertRaises(Exception):
            LoadBalancerBase(name='TestLB')

    def test_load_balancer_algorithm_choices(self):
        """测试负载算法枚举值"""
        for algorithm in ['round_robin', 'least_conn', 'source']:
            data = {'name': 'TestLB', 'vip_address': '192.168.1.1', 'algorithm': algorithm}
            schema = LoadBalancerBase(**data)
            self.assertEqual(schema.algorithm, algorithm)

    def test_load_balancer_status_choices(self):
        """测试状态枚举值"""
        for status in ['active', 'inactive']:
            data = {'name': 'TestLB', 'vip_address': '192.168.1.1', 'status': status}
            schema = LoadBalancerBase(**data)
            self.assertEqual(schema.status, status)


class LoadBalancerCreateRequestSchemaTest(TestCase):
    """LoadBalancer 创建请求测试"""

    def test_create_request_valid(self):
        """测试有效创建请求"""
        data = {
            'name': 'NewLB',
            'vip_address': '192.168.1.100',
            'port': 8080,
            'algorithm': 'least_conn',
            'status': 'active',
            'description': '新负载均衡器'
        }
        schema = LoadBalancerCreateRequest(**data)
        self.assertEqual(schema.name, 'NewLB')
        self.assertEqual(schema.vip_address, '192.168.1.100')
        self.assertEqual(schema.port, 8080)
        self.assertEqual(schema.algorithm, 'least_conn')

    def test_create_request_minimal(self):
        """测试最小创建请求"""
        schema = LoadBalancerCreateRequest(name='MinLB', vip_address='192.168.1.50')
        self.assertEqual(schema.name, 'MinLB')
        self.assertEqual(schema.vip_address, '192.168.1.50')


class LoadBalancerUpdateRequestSchemaTest(TestCase):
    """LoadBalancer 更新请求测试"""

    def test_update_request_valid(self):
        """测试有效更新请求"""
        data = {
            'name': 'UpdatedLB',
            'vip_address': '192.168.1.200',
            'port': 9090,
            'algorithm': 'source',
            'status': 'inactive',
            'description': '更新描述'
        }
        schema = LoadBalancerUpdateRequest(**data)
        self.assertEqual(schema.name, 'UpdatedLB')
        self.assertEqual(schema.vip_address, '192.168.1.200')
        self.assertEqual(schema.port, 9090)
        self.assertEqual(schema.algorithm, 'source')
        self.assertEqual(schema.status, 'inactive')
        self.assertEqual(schema.description, '更新描述')

    def test_update_request_partial(self):
        """测试部分更新请求"""
        data = {'name': 'PartialUpdate', 'status': 'inactive'}
        schema = LoadBalancerUpdateRequest(**data)
        self.assertEqual(schema.name, 'PartialUpdate')
        self.assertEqual(schema.status, 'inactive')
        # 未提供的字段应为 None
        self.assertIsNone(schema.vip_address)
        self.assertIsNone(schema.port)
        self.assertIsNone(schema.algorithm)

    def test_update_request_empty(self):
        """测试空更新请求"""
        schema = LoadBalancerUpdateRequest()
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.vip_address)
        self.assertIsNone(schema.port)


class LoadBalancerResponseSchemaTest(TestCase):
    """LoadBalancer 响应模型测试"""

    def test_response_valid(self):
        """测试有效响应模型"""
        data = {
            'id': 1,
            'name': 'ResponseLB',
            'vip_address': '192.168.1.100',
            'port': 80,
            'algorithm': 'round_robin',
            'status': 'active',
            'description': '响应描述',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LoadBalancerResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.name, 'ResponseLB')
        self.assertEqual(schema.vip_address, '192.168.1.100')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.algorithm, 'round_robin')
        self.assertEqual(schema.status, 'active')
        self.assertEqual(schema.description, '响应描述')
        self.assertEqual(schema.created_at, '2024-01-01T00:00:00Z')
        self.assertEqual(schema.updated_at, '2024-01-02T00:00:00Z')

    def test_response_minimal(self):
        """测试最小响应数据"""
        data = {
            'id': 2,
            'name': 'MinResponse',
            'vip_address': '10.0.0.1',
            'port': 80,
            'algorithm': 'round_robin',
            'status': 'active',
            'description': '',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LoadBalancerResponse(**data)
        self.assertEqual(schema.id, 2)
        self.assertEqual(schema.name, 'MinResponse')