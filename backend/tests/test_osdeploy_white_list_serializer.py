"""WhiteList Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import WhiteList
from backend.serializers.osdeploy import (
    WhiteListSerializer, WhiteListListSerializer,
    WhiteListCreateSerializer, WhiteListUpdateSerializer
)


class WhiteListSerializerTest(TestCase):
    """WhiteListSerializer 测试"""

    def setUp(self):
        self.whitelist = WhiteList.objects.create(
            mac_address='00:11:22:33:44:55',
            hostname='test-host',
            ip_address='192.168.1.50',
            description='Test whitelist entry',
            is_active=True
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = WhiteListSerializer(self.whitelist)
        data = serializer.data
        expected_fields = [
            'id', 'mac_address', 'hostname', 'ip_address',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = WhiteListListSerializer(self.whitelist)
        data = serializer.data
        expected_fields = ['id', 'mac_address', 'hostname', 'ip_address', 'is_active']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含description
        self.assertNotIn('description', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'mac_address': 'AA:BB:CC:DD:EE:FF',
            'hostname': 'new-host',
            'ip_address': '192.168.1.60',
            'description': 'New whitelist entry',
            'is_active': True
        }
        serializer = WhiteListCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_without_optional_fields(self):
        """测试创建序列化器允许省略可选字段"""
        data = {
            'mac_address': '11:22:33:44:55:66'
        }
        serializer = WhiteListCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'hostname': 'updated-host',
            'ip_address': '192.168.1.99',
            'is_active': False
        }
        serializer = WhiteListUpdateSerializer(self.whitelist, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'hostname': 'updated-host',
            'ip_address': '192.168.1.99',
            'is_active': False
        }
        serializer = WhiteListUpdateSerializer(self.whitelist, data=data, partial=True)
        self.assertTrue(serializer.is_valid())