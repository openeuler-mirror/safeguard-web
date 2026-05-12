"""KickStartFileStatus Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import KickStartFileStatus, RepoStatus
from backend.serializers.osdeploy import (
    KickStartFileStatusSerializer, KickStartFileStatusListSerializer,
    KickStartFileStatusCreateSerializer, KickStartFileStatusUpdateSerializer
)


class KickStartFileStatusSerializerTest(TestCase):
    """KickStartFileStatusSerializer 测试"""

    def setUp(self):
        self.repo = RepoStatus.objects.create(
            name='TestRepo',
            repo_type='yum',
            base_url='http://example.com/repo'
        )
        self.kickstart = KickStartFileStatus.objects.create(
            name='TestKickstart',
            content='url --url=http://example.com/centos\nkeyboard us',
            repo=self.repo,
            kernel_options={'ksdevice': 'eth0'},
            description='Test kickstart file'
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = KickStartFileStatusSerializer(self.kickstart)
        data = serializer.data
        expected_fields = [
            'id', 'name', 'content', 'repo', 'repo_name',
            'kernel_options', 'description', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_reads_repo_name(self):
        """测试序列化器正确读取关联的仓库名称"""
        serializer = KickStartFileStatusSerializer(self.kickstart)
        self.assertEqual(serializer.data['repo_name'], 'TestRepo')

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = KickStartFileStatusListSerializer(self.kickstart)
        data = serializer.data
        expected_fields = ['id', 'name', 'repo', 'repo_name']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含 content
        self.assertNotIn('content', data)

    def test_create_serializer_valid_data(self):
        """测试创建序列化器验证有效数据"""
        data = {
            'name': 'NewKickstart',
            'content': 'url --url=http://example.com/new\nkeyboard us',
            'repo': self.repo.id,
            'kernel_options': {'ksdevice': 'eth1'},
            'description': 'New kickstart file'
        }
        serializer = KickStartFileStatusCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_serializer_without_repo(self):
        """测试创建序列化器允许不关联仓库"""
        data = {
            'name': 'NoRepoKickstart',
            'content': 'url --url=http://example.com/centos',
            'repo': None
        }
        serializer = KickStartFileStatusCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_update_serializer_valid_data(self):
        """测试更新序列化器验证有效数据"""
        data = {
            'name': 'UpdatedKickstart',
            'description': 'Updated description'
        }
        serializer = KickStartFileStatusUpdateSerializer(self.kickstart, data=data, partial=True)
        self.assertTrue(serializer.is_valid())