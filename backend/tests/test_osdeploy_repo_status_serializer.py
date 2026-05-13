"""RepoStatus Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import RepoStatus
from backend.serializers.osdeploy import (
    RepoStatusSerializer, RepoStatusListSerializer,
    RepoStatusCreateSerializer, RepoStatusUpdateSerializer
)


class RepoStatusSerializerTest(TestCase):
    """RepoStatusSerializer 测试"""

    def setUp(self):
        self.repo = RepoStatus.objects.create(
            name='TestRepo',
            repo_type='yum',
            base_url='http://example.com/repo',
            is_default=True,
            description='Test repository'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = RepoStatusSerializer(self.repo)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'repo_type', 'base_url',
            'is_default', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = RepoStatusListSerializer(self.repo)
        data = serializer.data
        expected_fields = ['id', 'name', 'repo_type', 'is_default']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含详细字段
        self.assertNotIn('base_url', data)
        self.assertNotIn('description', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'name': 'NewRepo',
            'repo_type': 'http',
            'base_url': 'http://example.com/new',
            'is_default': False,
            'description': 'New repository'
        }
        serializer = RepoStatusCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_invalid_repo_type(self):
        """测试创建序列化器拒绝无效的仓库类型"""
        data = {
            'name': 'InvalidRepo',
            'repo_type': 'invalid_type',
            'base_url': 'http://example.com/invalid'
        }
        serializer = RepoStatusCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'name': 'UpdatedRepo',
            'description': 'Updated description'
        }
        serializer = RepoStatusUpdateSerializer(self.repo, data=data, partial=True)
        self.assertTrue(serializer.is_valid())