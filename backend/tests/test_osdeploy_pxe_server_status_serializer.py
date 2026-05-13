"""PXEServerStatus Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import PXEServerStatus
from backend.serializers.osdeploy import (
    PXEServerStatusSerializer, PXEServerStatusListSerializer,
    PXEServerStatusCreateSerializer, PXEServerStatusUpdateSerializer
)


class PXEServerStatusSerializerTest(TestCase):
    """PXEServerStatusSerializer 测试"""

    def setUp(self):
        self.pxe_server = PXEServerStatus.objects.create(
            server_ip='192.168.1.100',
            interface='eth0',
            dhcp_range_start='192.168.1.101',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active',
            description='Test PXE server'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = PXEServerStatusSerializer(self.pxe_server)
        data = serializer.data
        expected_fields = [
            'id', 'server_ip', 'interface', 'dhcp_range_start',
            'dhcp_range_end', 'subnet', 'gateway', 'status',
            'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = PXEServerStatusListSerializer(self.pxe_server)
        data = serializer.data
        expected_fields = ['id', 'server_ip', 'interface', 'status']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('dhcp_range_start', data)
        self.assertNotIn('gateway', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'server_ip': '192.168.1.200',
            'interface': 'eth1',
            'dhcp_range_start': '192.168.1.201',
            'dhcp_range_end': '192.168.1.250',
            'subnet': '255.255.255.0',
            'gateway': '192.168.1.1',
            'status': 'active',
            'description': 'New PXE server'
        }
        serializer = PXEServerStatusCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'interface': 'eth2',
            'status': 'inactive'
        }
        serializer = PXEServerStatusUpdateSerializer(self.pxe_server, data=data, partial=True)
        self.assertTrue(serializer.is_valid())