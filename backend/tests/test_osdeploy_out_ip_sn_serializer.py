"""OutIpSN Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import OutIpSN
from backend.serializers.osdeploy import (
    OutIpSNSerializer, OutIpSNListSerializer,
    OutIpSNCreateSerializer, OutIpSNUpdateSerializer
)


class OutIpSNSerializerTest(TestCase):
    """OutIpSNSerializer 测试"""

    def setUp(self):
        self.out_ip_sn = OutIpSN.objects.create(
            mac_address='00:11:22:33:44:55',
            sn='SN123456789',
            description='Test out IP SN'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = OutIpSNSerializer(self.out_ip_sn)
        data = serializer.data
        expected_fields = [
            'id', 'mac_address', 'sn', 'description',
            'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = OutIpSNListSerializer(self.out_ip_sn)
        data = serializer.data
        expected_fields = ['id', 'mac_address', 'sn']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含description
        self.assertNotIn('description', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'mac_address': 'AA:BB:CC:DD:EE:FF',
            'sn': 'NEWSN123456',
            'description': 'New out IP SN'
        }
        serializer = OutIpSNCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_mac_unique(self):
        """测试创建序列化器验证MAC地址唯一性"""
        data = {
            'mac_address': '00:11:22:33:44:55',  # 已存在
            'sn': 'UNIQUESN123'
        }
        serializer = OutIpSNCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'sn': 'UPDATEDSN123',
            'description': 'Updated description'
        }
        serializer = OutIpSNUpdateSerializer(self.out_ip_sn, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_only_allows_certain_fields(self):
        """测试更新序列化器只允许更新特定字段"""
        data = {
            'mac_address': 'FF:FF:FF:FF:FF:FF'  # 不允许更新
        }
        serializer = OutIpSNUpdateSerializer(self.out_ip_sn, data=data, partial=True)
        self.assertFalse(serializer.is_valid())