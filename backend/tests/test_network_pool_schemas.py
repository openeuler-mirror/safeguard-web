"""LBPool Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.network.lb_pool import (
    LBPoolBase,
    LBPoolCreateRequest,
    LBPoolUpdateRequest,
    LBPoolResponse,
)


class LBPoolBaseSchemaTest(TestCase):
    """LBPool 基础模型测试"""

    def test_pool_base_valid(self):
        """测试有效的后端池基础模型"""
        data = {
            'name': 'TestPool',
            'loadbalancer': 1,
            'protocol': 'tcp',
            'description': '测试后端池'
        }
        schema = LBPoolBase(**data)
        self.assertEqual(schema.name, 'TestPool')
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.description, '测试后端池')

    def test_pool_base_minimal(self):
        """测试最小后端池数据"""
        schema = LBPoolBase(name='MinimalPool', loadbalancer=1, protocol='http')
        self.assertEqual(schema.name, 'MinimalPool')
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'http')
        self.assertEqual(schema.description, '')

    def test_pool_base_default_values(self):
        """测试后端池默认值"""
        schema = LBPoolBase(name='DefaultPool', loadbalancer=1, protocol='tcp')
        self.assertEqual(schema.description, '')

    def test_pool_name_required(self):
        """测试名称为必填"""
        with self.assertRaises(Exception):
            LBPoolBase(loadbalancer=1, protocol='tcp')

    def test_pool_loadbalancer_required(self):
        """测试负载均衡器ID为必填"""
        with self.assertRaises(Exception):
            LBPoolBase(name='TestPool', protocol='tcp')

    def test_pool_protocol_required(self):
        """测试协议为必填"""
        with self.assertRaises(Exception):
            LBPoolBase(name='TestPool', loadbalancer=1)

    def test_pool_name_max_length(self):
        """测试名称最大长度"""
        data = {'name': 'x' * 100, 'loadbalancer': 1, 'protocol': 'tcp'}
        schema = LBPoolBase(**data)
        self.assertEqual(schema.name, 'x' * 100)

    def test_pool_protocol_choices(self):
        """测试协议枚举值"""
        for protocol in ['tcp', 'http', 'https']:
            data = {'name': 'TestPool', 'loadbalancer': 1, 'protocol': protocol}
            schema = LBPoolBase(**data)
            self.assertEqual(schema.protocol, protocol)


class LBPoolCreateRequestSchemaTest(TestCase):
    """LBPool 创建请求测试"""

    def test_create_request_valid(self):
        """测试有效创建请求"""
        data = {
            'name': 'NewPool',
            'loadbalancer': 1,
            'protocol': 'https',
            'description': '新后端池'
        }
        schema = LBPoolCreateRequest(**data)
        self.assertEqual(schema.name, 'NewPool')
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'https')
        self.assertEqual(schema.description, '新后端池')

    def test_create_request_minimal(self):
        """测试最小创建请求"""
        schema = LBPoolCreateRequest(name='MinPool', loadbalancer=1, protocol='tcp')
        self.assertEqual(schema.name, 'MinPool')
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'tcp')


class LBPoolUpdateRequestSchemaTest(TestCase):
    """LBPool 更新请求测试"""

    def test_update_request_valid(self):
        """测试有效更新请求"""
        data = {
            'name': 'UpdatedPool',
            'protocol': 'http',
            'description': '更新描述'
        }
        schema = LBPoolUpdateRequest(**data)
        self.assertEqual(schema.name, 'UpdatedPool')
        self.assertEqual(schema.protocol, 'http')
        self.assertEqual(schema.description, '更新描述')

    def test_update_request_partial(self):
        """测试部分更新请求"""
        data = {'name': 'PartialUpdate'}
        schema = LBPoolUpdateRequest(**data)
        self.assertEqual(schema.name, 'PartialUpdate')
        # 未提供的字段应为 None
        self.assertIsNone(schema.protocol)
        self.assertIsNone(schema.description)

    def test_update_request_empty(self):
        """测试空更新请求"""
        schema = LBPoolUpdateRequest()
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.protocol)
        self.assertIsNone(schema.description)

    def test_update_request_protocol_only(self):
        """测试仅更新协议"""
        data = {'protocol': 'https'}
        schema = LBPoolUpdateRequest(**data)
        self.assertEqual(schema.protocol, 'https')
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.description)


class LBPoolResponseSchemaTest(TestCase):
    """LBPool 响应模型测试"""

    def test_response_valid(self):
        """测试有效响应模型"""
        data = {
            'id': 1,
            'name': 'ResponsePool',
            'loadbalancer': 1,
            'loadbalancer_name': 'TestLB',
            'protocol': 'tcp',
            'description': '响应描述',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBPoolResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.name, 'ResponsePool')
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.loadbalancer_name, 'TestLB')
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.description, '响应描述')
        self.assertEqual(schema.created_at, '2024-01-01T00:00:00Z')
        self.assertEqual(schema.updated_at, '2024-01-02T00:00:00Z')

    def test_response_minimal(self):
        """测试最小响应数据"""
        data = {
            'id': 2,
            'name': 'MinResponse',
            'loadbalancer': 1,
            'loadbalancer_name': None,
            'protocol': 'http',
            'description': '',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBPoolResponse(**data)
        self.assertEqual(schema.id, 2)
        self.assertEqual(schema.name, 'MinResponse')
        self.assertIsNone(schema.loadbalancer_name)