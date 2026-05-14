"""JobStatus 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.osdeploy import JobStatus


class JobViewSetTest(APITestCase):
    """JobViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_job',
            password='testpass123',
            nickname='测试用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_jobs(self):
        """测试列出任务"""
        JobStatus.objects.create(
            job_id='job-001',
            job_type='os_install',
            target='host_1',
            status='pending'
        )
        JobStatus.objects.create(
            job_id='job-002',
            job_type='os_install',
            target='host_2',
            status='success'
        )
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_retrieve_job(self):
        """测试获取单个任务"""
        job = JobStatus.objects.create(
            job_id='job-test-001',
            job_type='os_install',
            target='host_1',
            status='running',
            progress=50
        )
        response = self.client.get(f'/api/jobs/{job.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['job_id'], 'job-test-001')
        self.assertEqual(response.data['data']['progress'], 50)

    def test_query_job_by_job_id(self):
        """测试通过query action查询任务"""
        job = JobStatus.objects.create(
            job_id='job-query-001',
            job_type='os_install',
            target='host_1',
            status='success'
        )
        response = self.client.get('/api/jobs/query/', {'job_id': 'job-query-001'})
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['job_id'], 'job-query-001')

    def test_query_job_not_found(self):
        """测试查询不存在的任务"""
        response = self.client.get('/api/jobs/query/', {'job_id': 'non-existent'})
        self.assertNotEqual(response.data['errno'], 0)
        self.assertIn('不存在', response.data['errmsg'])

    def test_query_job_without_job_id(self):
        """测试查询时不传job_id"""
        response = self.client.get('/api/jobs/query/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_filter_jobs_by_status(self):
        """测试按状态过滤任务"""
        JobStatus.objects.create(
            job_id='job-pending',
            job_type='os_install',
            target='host_1',
            status='pending'
        )
        JobStatus.objects.create(
            job_id='job-success',
            job_type='os_install',
            target='host_2',
            status='success'
        )
        response = self.client.get('/api/jobs/', {'status': 'pending'})
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'pending')

    def test_filter_jobs_by_job_type(self):
        """测试按任务类型过滤"""
        JobStatus.objects.create(
            job_id='job-install',
            job_type='os_install',
            target='host_1',
            status='pending'
        )
        JobStatus.objects.create(
            job_id='job-migrate',
            job_type='os_migrate',
            target='host_2',
            status='pending'
        )
        response = self.client.get('/api/jobs/', {'job_type': 'os_install'})
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['job_type'], 'os_install')