"""JobStatus Serializer 测试"""
from django.test import TestCase
from backend.models.osdeploy import JobStatus
from backend.serializers.osdeploy import JobStatusSerializer, JobStatusListSerializer


class JobStatusSerializerTest(TestCase):
    """JobStatusSerializer 测试"""

    def setUp(self):
        self.job = JobStatus.objects.create(
            job_id='test-job-001',
            job_type='os_install',
            target='host_1',
            status='running',
            progress=50,
            result={'ip': '192.168.1.100'},
            error_message=''
        )

    def test_serializer_contains_expected_fields(self):
        """测试序列化器包含预期字段"""
        serializer = JobStatusSerializer(self.job)
        data = serializer.data
        expected_fields = [
            'id', 'job_id', 'job_type', 'target', 'status',
            'progress', 'result', 'error_message',
            'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_valid_data(self):
        """测试序列化器验证有效数据"""
        data = {
            'job_id': 'new-job-001',
            'job_type': 'os_install',
            'target': 'host_2',
            'status': 'pending'
        }
        serializer = JobStatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_list_serializer_contains_expected_fields(self):
        """测试列表序列化器包含预期字段"""
        serializer = JobStatusListSerializer(self.job)
        data = serializer.data
        expected_fields = ['id', 'job_id', 'job_type', 'target', 'status', 'progress', 'created_at']
        for field in expected_fields:
            self.assertIn(field, data)
        # 列表序列化器不应包含 detail 字段
        self.assertNotIn('result', data)
        self.assertNotIn('error_message', data)