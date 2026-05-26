"""LBHealthMonitor Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.network.lb_health_monitor import (
    LBHealthMonitorBase,
    LBHealthMonitorCreateRequest,
    LBHealthMonitorUpdateRequest,
    LBHealthMonitorResponse,
)


class LBHealthMonitorBaseSchemaTest(TestCase):
    """LBHealthMonitor 基础模型测试"""

    def test_health_monitor_base_valid(self):
        """测试有效的健康检查基础模型"""
        data = {
            'pool': 1,
            'monitor_type': 'tcp',
            'interval': 10,
            'timeout': 5,
            'retry': 3,
            'description': '测试健康检查'
        }
        schema = LBHealthMonitorBase(**data)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.monitor_type, 'tcp')
        self.assertEqual(schema.interval, 10)
        self.assertEqual(schema.timeout, 5)
        self.assertEqual(schema.retry, 3)
        self.assertEqual(schema.description, '测试健康检查')

    def test_health_monitor_base_minimal(self):
        """测试最小健康检查数据"""
        schema = LBHealthMonitorBase(pool=1, monitor_type='http')
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.monitor_type, 'http')
        self.assertEqual(schema.interval, 5)  # 默认值
        self.assertEqual(schema.timeout, 3)  # 默认值
        self.assertEqual(schema.retry, 3)  # 默认值
        self.assertEqual(schema.description, '')

    def test_health_monitor_base_default_values(self):
        """测试健康检查默认值"""
        schema = LBHealthMonitorBase(pool=1, monitor_type='ping')
        self.assertEqual(schema.interval, 5)
        self.assertEqual(schema.timeout, 3)
        self.assertEqual(schema.retry, 3)
        self.assertEqual(schema.description, '')

    def test_health_monitor_pool_required(self):
        """测试后端池ID为必填"""
        with self.assertRaises(Exception):
            LBHealthMonitorBase(monitor_type='tcp')

    def test_health_monitor_type_required(self):
        """测试检查类型为必填"""
        with self.assertRaises(Exception):
            LBHealthMonitorBase(pool=1)

    def test_health_monitor_type_choices(self):
        """测试检查类型枚举值"""
        for monitor_type in ['tcp', 'http', 'ping']:
            data = {'pool': 1, 'monitor_type': monitor_type}
            schema = LBHealthMonitorBase(**data)
            self.assertEqual(schema.monitor_type, monitor_type)

    def test_health_monitor_interval_choices(self):
        """测试检查间隔枚举值"""
        intervals = [5, 10, 15, 30, 60]
        for interval in intervals:
            data = {'pool': 1, 'monitor_type': 'tcp', 'interval': interval}
            schema = LBHealthMonitorBase(**data)
            self.assertEqual(schema.interval, interval)

    def test_health_monitor_timeout_choices(self):
        """测试超时枚举值"""
        timeouts = [3, 5, 10, 15]
        for timeout in timeouts:
            data = {'pool': 1, 'monitor_type': 'tcp', 'timeout': timeout}
            schema = LBHealthMonitorBase(**data)
            self.assertEqual(schema.timeout, timeout)

    def test_health_monitor_retry_choices(self):
        """测试重试次数枚举值"""
        retries = [1, 2, 3, 5]
        for retry in retries:
            data = {'pool': 1, 'monitor_type': 'tcp', 'retry': retry}
            schema = LBHealthMonitorBase(**data)
            self.assertEqual(schema.retry, retry)


class LBHealthMonitorCreateRequestSchemaTest(TestCase):
    """LBHealthMonitor 创建请求测试"""

    def test_create_request_valid(self):
        """测试有效创建请求"""
        data = {
            'pool': 1,
            'monitor_type': 'http',
            'interval': 15,
            'timeout': 5,
            'retry': 3,
            'description': '新健康检查'
        }
        schema = LBHealthMonitorCreateRequest(**data)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.monitor_type, 'http')
        self.assertEqual(schema.interval, 15)
        self.assertEqual(schema.timeout, 5)
        self.assertEqual(schema.retry, 3)

    def test_create_request_minimal(self):
        """测试最小创建请求"""
        schema = LBHealthMonitorCreateRequest(pool=1, monitor_type='tcp')
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.monitor_type, 'tcp')
        self.assertEqual(schema.interval, 5)  # 默认值


class LBHealthMonitorUpdateRequestSchemaTest(TestCase):
    """LBHealthMonitor 更新请求测试"""

    def test_update_request_valid(self):
        """测试有效更新请求"""
        data = {
            'monitor_type': 'http',
            'interval': 20,
            'timeout': 10,
            'retry': 5,
            'description': '更新描述'
        }
        schema = LBHealthMonitorUpdateRequest(**data)
        self.assertEqual(schema.monitor_type, 'http')
        self.assertEqual(schema.interval, 20)
        self.assertEqual(schema.timeout, 10)
        self.assertEqual(schema.retry, 5)
        self.assertEqual(schema.description, '更新描述')

    def test_update_request_partial(self):
        """测试部分更新请求"""
        data = {'interval': 30}
        schema = LBHealthMonitorUpdateRequest(**data)
        self.assertEqual(schema.interval, 30)
        # 未提供的字段应为 None
        self.assertIsNone(schema.monitor_type)
        self.assertIsNone(schema.timeout)

    def test_update_request_empty(self):
        """测试空更新请求"""
        schema = LBHealthMonitorUpdateRequest()
        self.assertIsNone(schema.monitor_type)
        self.assertIsNone(schema.interval)
        self.assertIsNone(schema.timeout)

    def test_update_request_type_only(self):
        """测试仅更新检查类型"""
        data = {'monitor_type': 'ping'}
        schema = LBHealthMonitorUpdateRequest(**data)
        self.assertEqual(schema.monitor_type, 'ping')
        self.assertIsNone(schema.interval)

    def test_update_request_retry_only(self):
        """测试仅更新重试次数"""
        data = {'retry': 5}
        schema = LBHealthMonitorUpdateRequest(**data)
        self.assertEqual(schema.retry, 5)
        self.assertIsNone(schema.monitor_type)


class LBHealthMonitorResponseSchemaTest(TestCase):
    """LBHealthMonitor 响应模型测试"""

    def test_response_valid(self):
        """测试有效响应模型"""
        data = {
            'id': 1,
            'pool': 1,
            'pool_name': 'TestPool',
            'monitor_type': 'tcp',
            'interval': 10,
            'timeout': 5,
            'retry': 3,
            'description': '响应描述',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBHealthMonitorResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.pool, 1)
        self.assertEqual(schema.pool_name, 'TestPool')
        self.assertEqual(schema.monitor_type, 'tcp')
        self.assertEqual(schema.interval, 10)
        self.assertEqual(schema.timeout, 5)
        self.assertEqual(schema.retry, 3)
        self.assertEqual(schema.description, '响应描述')
        self.assertEqual(schema.created_at, '2024-01-01T00:00:00Z')
        self.assertEqual(schema.updated_at, '2024-01-02T00:00:00Z')

    def test_response_minimal(self):
        """测试最小响应数据"""
        data = {
            'id': 2,
            'pool': 1,
            'pool_name': None,
            'monitor_type': 'http',
            'interval': 5,
            'timeout': 3,
            'retry': 3,
            'description': '',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = LBHealthMonitorResponse(**data)
        self.assertEqual(schema.id, 2)
        self.assertIsNone(schema.pool_name)