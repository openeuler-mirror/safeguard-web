"""LBListener Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.network.lb_listener import (
    LBListenerBase,
    LBListenerCreateRequest,
    LBListenerUpdateRequest,
    LBListenerResponse,
)


class LBListenerBaseSchemaTest(TestCase):
    """LBListener 基础模型测试"""

    def test_listener_base_valid(self):
        """测试有效的监听器基础模型"""
        data = {
            'loadbalancer': 1,
            'protocol': 'tcp',
            'port': 80,
            'name': 'TestListener',
            'description': '测试监听器'
        }
        schema = LBListenerBase(**data)
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.name, 'TestListener')
        self.assertEqual(schema.description, '测试监听器')

    def test_listener_base_minimal(self):
        """测试最小监听器数据"""
        schema = LBListenerBase(loadbalancer=1, protocol='tcp', port=8080)
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.port, 8080)
        self.assertEqual(schema.name, '')
        self.assertEqual(schema.description, '')

    def test_listener_base_default_values(self):
        """测试监听器默认值"""
        schema = LBListenerBase(loadbalancer=1, protocol='http', port=443)
        self.assertEqual(schema.name, '')
        self.assertEqual(schema.description, '')

    def test_listener_loadbalancer_required(self):
        """测试负载均衡器ID为必填"""
        with self.assertRaises(Exception):
            LBListenerBase(protocol='tcp', port=80)

    def test_listener_protocol_required(self):
        """测试协议为必填"""
        with self.assertRaises(Exception):
            LBListenerBase(loadbalancer=1, port=80)

    def test_listener_port_required(self):
        """测试端口为必填"""
        with self.assertRaises(Exception):
            LBListenerBase(loadbalancer=1, protocol='tcp')

    def test_listener_protocol_choices(self):
        """测试协议枚举值"""
        for protocol in ['tcp', 'http', 'https']:
            data = {'loadbalancer': 1, 'protocol': protocol, 'port': 80}
            schema = LBListenerBase(**data)
            self.assertEqual(schema.protocol, protocol)

    def test_listener_name_optional(self):
        """测试名称为可选"""
        schema = LBListenerBase(loadbalancer=1, protocol='tcp', port=80)
        self.assertEqual(schema.name, '')

    def test_listener_name_max_length(self):
        """测试名称最大长度"""
        data = {'loadbalancer': 1, 'protocol': 'tcp', 'port': 80, 'name': 'x' * 100}
        schema = LBListenerBase(**data)
        self.assertEqual(schema.name, 'x' * 100)


class LBListenerCreateRequestSchemaTest(TestCase):
    """LBListener 创建请求测试"""

    def test_create_request_valid(self):
        """测试有效创建请求"""
        data = {
            'loadbalancer': 1,
            'protocol': 'https',
            'port': 443,
            'name': 'NewListener',
            'description': '新监听器'
        }
        schema = LBListenerCreateRequest(**data)
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'https')
        self.assertEqual(schema.port, 443)
        self.assertEqual(schema.name, 'NewListener')

    def test_create_request_minimal(self):
        """测试最小创建请求"""
        schema = LBListenerCreateRequest(loadbalancer=1, protocol='tcp', port=8080)
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.port, 8080)


class LBListenerUpdateRequestSchemaTest(TestCase):
    """LBListener 更新请求测试"""

    def test_update_request_valid(self):
        """测试有效更新请求"""
        data = {
            'protocol': 'http',
            'port': 9090,
            'name': 'UpdatedListener',
            'description': '更新描述'
        }
        schema = LBListenerUpdateRequest(**data)
        self.assertEqual(schema.protocol, 'http')
        self.assertEqual(schema.port, 9090)
        self.assertEqual(schema.name, 'UpdatedListener')
        self.assertEqual(schema.description, '更新描述')

    def test_update_request_partial(self):
        """测试部分更新请求"""
        data = {'port': 8888}
        schema = LBListenerUpdateRequest(**data)
        self.assertEqual(schema.port, 8888)
        # 未提供的字段应为 None
        self.assertIsNone(schema.protocol)
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.description)

    def test_update_request_empty(self):
        """测试空更新请求"""
        schema = LBListenerUpdateRequest()
        self.assertIsNone(schema.protocol)
        self.assertIsNone(schema.port)
        self.assertIsNone(schema.name)
        self.assertIsNone(schema.description)

    def test_update_request_name_only(self):
        """测试仅更新名称"""
        data = {'name': 'NameOnlyUpdate'}
        schema = LBListenerUpdateRequest(**data)
        self.assertEqual(schema.name, 'NameOnlyUpdate')
        self.assertIsNone(schema.protocol)
        self.assertIsNone(schema.port)


class LBListenerResponseSchemaTest(TestCase):
    """LBListener 响应模型测试"""

    def test_response_valid(self):
        """测试有效响应模型"""
        data = {
            'id': 1,
            'loadbalancer': 1,
            'loadbalancer_name': 'TestLB',
            'protocol': 'tcp',
            'port': 80,
            'name': 'ResponseListener',
            'description': '响应描述',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBListenerResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.loadbalancer, 1)
        self.assertEqual(schema.loadbalancer_name, 'TestLB')
        self.assertEqual(schema.protocol, 'tcp')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.name, 'ResponseListener')
        self.assertEqual(schema.description, '响应描述')
        self.assertEqual(schema.created_at, '2024-01-01T00:00:00Z')
        self.assertEqual(schema.updated_at, '2024-01-02T00:00:00Z')

    def test_response_minimal(self):
        """测试最小响应数据"""
        data = {
            'id': 2,
            'loadbalancer': 1,
            'loadbalancer_name': None,
            'protocol': 'http',
            'port': 8080,
            'name': '',
            'description': '',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBListenerResponse(**data)
        self.assertEqual(schema.id, 2)
        self.assertIsNone(schema.loadbalancer_name)