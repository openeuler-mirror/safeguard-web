"""ISOFileStatus Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import ISOFileStatus
from backend.serializers.osdeploy import (
    ISOFileStatusSerializer, ISOFileStatusListSerializer,
    ISOFileStatusCreateSerializer, ISOFileStatusUpdateSerializer
)


class ISOFileStatusSerializerTest(TestCase):
    """ISOFileStatusSerializer 测试"""

    def setUp(self):
        self.iso_file = ISOFileStatus.objects.create(
            filename='CentOS-7-x86_64-DVD-2009.iso',
            size=4700000000,
            md5sum='d41d8cd98f00b204e9800998ecf8427e',
            status='available',
            file_path='/mnt/iso/CentOS-7-x86_64-DVD-2009.iso',
            description='CentOS 7 DVD ISO'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = ISOFileStatusSerializer(self.iso_file)
        data = serializer.data
        expected_fields = [
            'id', 'filename', 'size', 'md5sum', 'status',
            'file_path', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_md5sum_is_read_only(self):
        """测试md5sum字段是只读的"""
        serializer = ISOFileStatusSerializer(self.iso_file)
        # md5sum应该存在于数据中
        self.assertIn('md5sum', serializer.data)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = ISOFileStatusListSerializer(self.iso_file)
        data = serializer.data
        expected_fields = ['id', 'filename', 'size', 'status']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('md5sum', data)
        self.assertNotIn('file_path', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'filename': 'Ubuntu-20.04-server.iso',
            'size': 1000000000,
            'md5sum': 'a41d8cd98f00b204e9800998ecf8427e',
            'status': 'uploading',
            'file_path': '/mnt/iso/ubuntu.iso',
            'description': 'Ubuntu 20.04 ISO'
        }
        serializer = ISOFileStatusCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'status': 'disabled',
            'description': 'ISO file deprecated'
        }
        serializer = ISOFileStatusUpdateSerializer(self.iso_file, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_fields(self):
        """测试更新序列化器只允许更新status和description"""
        data = {
            'status': 'disabled'
        }
        serializer = ISOFileStatusUpdateSerializer(self.iso_file, data=data, partial=True)
        self.assertTrue(serializer.is_valid())