"""LBMember Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.network.lb_member import (
    LBMemberBase,
    LBMemberCreateRequest,
    LBMemberUpdateRequest,
    LBMemberResponse,
)


class LBMemberBaseSchemaTest(TestCase):
    """LBMember 基础模型测试"""

    def test_member_base_valid(self):
        """测试有效的池成员基础模型"""
        data = {
            'pool': 1,
            'address': '192.168.1.100',
            'port': 8080,
            'weight': 10,
            'is_enabled': True,
            'description': '测试池成员'
        }
        schema = LBMemberBase(**data)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.address, '192.168.1.100')
        self.assertEqual(schema.port, 8080)
        self.assertEqual(schema.weight, 10)
        self.assertEqual(schema.is_enabled, True)
        self.assertEqual(schema.description, '测试池成员')

    def test_member_base_minimal(self):
        """测试最小池成员数据"""
        schema = LBMemberBase(pool=1, address='192.168.1.50', port=80)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.address, '192.168.1.50')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.weight, 1)  # 默认权重
        self.assertEqual(schema.is_enabled, True)  # 默认启用
        self.assertEqual(schema.description, '')

    def test_member_base_default_values(self):
        """测试池成员默认值"""
        schema = LBMemberBase(pool=1, address='10.0.0.1', port=443)
        self.assertEqual(schema.weight, 1)
        self.assertEqual(schema.is_enabled, True)
        self.assertEqual(schema.description, '')

    def test_member_pool_required(self):
        """测试后端池ID为必填"""
        with self.assertRaises(Exception):
            LBMemberBase(address='192.168.1.1', port=80)

    def test_member_address_required(self):
        """测试成员地址为必填"""
        with self.assertRaises(Exception):
            LBMemberBase(pool=1, port=80)

    def test_member_port_required(self):
        """测试端口为必填"""
        with self.assertRaises(Exception):
            LBMemberBase(pool=1, address='192.168.1.1')

    def test_member_address_validation(self):
        """测试成员地址格式验证"""
        # 有效的IP地址
        valid_addresses = ['192.168.1.1', '10.0.0.1', '172.16.0.100']
        for addr in valid_addresses:
            data = {'pool': 1, 'address': addr, 'port': 80}
            schema = LBMemberBase(**data)
            self.assertEqual(schema.address, addr)

    def test_member_weight_range(self):
        """测试权重范围"""
        data = {'pool': 1, 'address': '192.168.1.1', 'port': 80, 'weight': 50}
        schema = LBMemberBase(**data)
        self.assertEqual(schema.weight, 50)


class LBMemberCreateRequestSchemaTest(TestCase):
    """LBMember 创建请求测试"""

    def test_create_request_valid(self):
        """测试有效创建请求"""
        data = {
            'pool': 1,
            'address': '192.168.1.100',
            'port': 8080,
            'weight': 20,
            'is_enabled': False,
            'description': '新池成员'
        }
        schema = LBMemberCreateRequest(**data)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.address, '192.168.1.100')
        self.assertEqual(schema.port, 8080)
        self.assertEqual(schema.weight, 20)
        self.assertEqual(schema.is_enabled, False)

    def test_create_request_minimal(self):
        """测试最小创建请求"""
        schema = LBMemberCreateRequest(pool=1, address='192.168.1.50', port=80)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.address, '192.168.1.50')
        self.assertEqual(schema.port, 80)
        self.assertEqual(schema.weight, 1)  # 默认值
        self.assertEqual(schema.is_enabled, True)  # 默认值


class LBMemberUpdateRequestSchemaTest(TestCase):
    """LBMember 更新请求测试"""

    def test_update_request_valid(self):
        """测试有效更新请求"""
        data = {
            'address': '192.168.1.200',
            'port': 9090,
            'weight': 30,
            'is_enabled': False,
            'description': '更新描述'
        }
        schema = LBMemberUpdateRequest(**data)
        self.assertEqual(schema.address, '192.168.1.200')
        self.assertEqual(schema.port, 9090)
        self.assertEqual(schema.weight, 30)
        self.assertEqual(schema.is_enabled, False)
        self.assertEqual(schema.description, '更新描述')

    def test_update_request_partial(self):
        """测试部分更新请求"""
        data = {'weight': 50}
        schema = LBMemberUpdateRequest(**data)
        self.assertEqual(schema.weight, 50)
        # 未提供的字段应为 None
        self.assertIsNone(schema.address)
        self.assertIsNone(schema.port)
        self.assertIsNone(schema.is_enabled)

    def test_update_request_empty(self):
        """测试空更新请求"""
        schema = LBMemberUpdateRequest()
        self.assertIsNone(schema.address)
        self.assertIsNone(schema.port)
        self.assertIsNone(schema.weight)
        self.assertIsNone(schema.is_enabled)

    def test_update_request_address_only(self):
        """测试仅更新地址"""
        data = {'address': '10.0.0.100'}
        schema = LBMemberUpdateRequest(**data)
        self.assertEqual(schema.address, '10.0.0.100')
        self.assertIsNone(schema.port)

    def test_update_request_enable_only(self):
        """测试仅更新启用状态"""
        data = {'is_enabled': True}
        schema = LBMemberUpdateRequest(**data)
        self.assertEqual(schema.is_enabled, True)
        self.assertIsNone(schema.weight)


class LBMemberResponseSchemaTest(TestCase):
    """LBMember 响应模型测试"""

    def test_response_valid(self):
        """测试有效响应模型"""
        data = {
            'id': 1,
            'pool': 1,
            'pool_name': 'TestPool',
            'address': '192.168.1.100',
            'port': 8080,
            'weight': 10,
            'is_enabled': True,
            'description': '响应描述',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBMemberResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.pool_name, 'TestPool')
        self.assertEqual(schema.address, '192.168.1.100')
        self.assertEqual(schema.port, 8080)
        self.assertEqual(schema.weight, 10)
        self.assertEqual(schema.is_enabled, True)
        self.assertEqual(schema.description, '响应描述')
        self.assertEqual(schema.created_at, '2024-01-01T00:00:00Z')
        self.assertEqual(schema.updated_at, '2024-01-02T00:00:00Z')

    def test_response_minimal(self):
        """测试最小响应数据"""
        data = {
            'id': 2,
            'pool': 1,
            'pool_name': None,
            'address': '10.0.0.1',
            'port': 443,
            'weight': 1,
            'is_enabled': True,
            'description': '',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBMemberResponse(**data)
        self.assertEqual(schema.id, 2)
        self.assertIsNone(schema.pool_name)
        self.assertEqual(schema.weight, 1)