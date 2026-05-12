"""DeployService 测试"""
from django.test import TestCase
from backend.models.osdeploy import JobStatus, RepoStatus, KickStartFileStatus
from backend.services.osdeploy import DeployService


class DeployServiceTest(TestCase):
    """DeployService 测试"""

    def setUp(self):
        self.repo = RepoStatus.objects.create(
            name='TestRepo',
            repo_type='yum',
            base_url='http://example.com/repo',
            is_default=True
        )
        self.kickstart = KickStartFileStatus.objects.create(
            name='TestKickstart',
            content='url --url={{{repo_url}}}\nkeyboard us\nlang en_US\nrootpw {{{password}}}',
            repo=self.repo,
            kernel_options={'ksdevice': 'eth0'}
        )

    def test_generate_kickstart(self):
        """测试生成Kickstart文件"""
        content = DeployService.generate_kickstart(self.kickstart.id, {
            'repo_url': 'http://example.com/centos',
            'password': 'secret123'
        })
        self.assertIn('http://example.com/centos', content)
        self.assertIn('secret123', content)
        self.assertNotIn('{{{repo_url}}}', content)

    def test_generate_kickstart_not_found(self):
        """测试生成不存在的Kickstart模板"""
        with self.assertRaises(ValueError):
            DeployService.generate_kickstart(9999, {})

    def test_start_auto_install(self):
        """测试启动自动安装任务"""
        job = DeployService.start_auto_install(
            host_id=1,
            kickstart_id=self.kickstart.id,
            repo_id=self.repo.id
        )
        self.assertIsNotNone(job)
        self.assertTrue(job.job_id.startswith('install-'))
        self.assertEqual(job.job_type, 'os_install')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)

    def test_start_auto_install_invalid_kickstart(self):
        """测试启动自动安装-无效的kickstart"""
        with self.assertRaises(ValueError):
            DeployService.start_auto_install(
                host_id=1,
                kickstart_id=9999,
                repo_id=self.repo.id
            )

    def test_start_auto_install_invalid_repo(self):
        """测试启动自动安装-无效的repo"""
        with self.assertRaises(ValueError):
            DeployService.start_auto_install(
                host_id=1,
                kickstart_id=self.kickstart.id,
                repo_id=9999
            )

    def test_query_job_status(self):
        """测试查询任务状态"""
        JobStatus.objects.create(
            job_id='test-job-001',
            job_type='os_install',
            target='host_1',
            status='running'
        )
        result = DeployService.query_job_status('test-job-001')
        self.assertIsNotNone(result)
        self.assertEqual(result.job_id, 'test-job-001')

    def test_query_job_status_not_found(self):
        """测试查询不存在的任务"""
        result = DeployService.query_job_status('non-existent')
        self.assertIsNone(result)

    def test_list_jobs(self):
        """测试获取任务列表"""
        JobStatus.objects.create(
            job_id='list-job-1',
            job_type='os_install',
            target='host_1',
            status='pending'
        )
        JobStatus.objects.create(
            job_id='list-job-2',
            job_type='hardware_collect',
            target='host_2',
            status='success'
        )
        result = DeployService.list_jobs()
        self.assertEqual(result['total'], 2)

    def test_list_jobs_with_pagination(self):
        """测试任务列表分页"""
        for i in range(15):
            JobStatus.objects.create(
                job_id=f'page-job-{i}',
                job_type='os_install',
                target=f'host_{i}'
            )
        result = DeployService.list_jobs(page=1, page_size=5)
        self.assertEqual(result['total'], 15)
        self.assertEqual(len(result['results']), 5)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 5)

    def test_list_jobs_with_filter(self):
        """测试任务列表过滤"""
        JobStatus.objects.create(
            job_id='filter-job',
            job_type='os_install',
            target='host_filter',
            status='failed'
        )
        result = DeployService.list_jobs(filters={'status': 'failed'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].job_id, 'filter-job')

    def test_update_job_status(self):
        """测试更新任务状态"""
        JobStatus.objects.create(
            job_id='update-job',
            job_type='os_install',
            target='host_1',
            status='pending'
        )
        updated = DeployService.update_job_status(
            job_id='update-job',
            status='running',
            progress=50
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, 'running')
        self.assertEqual(updated.progress, 50)

    def test_update_job_status_with_error(self):
        """测试更新任务状态-包含错误信息"""
        JobStatus.objects.create(
            job_id='error-job',
            job_type='os_install',
            target='host_1',
            status='running'
        )
        updated = DeployService.update_job_status(
            job_id='error-job',
            status='failed',
            error_message='Installation failed: network error'
        )
        self.assertEqual(updated.status, 'failed')
        self.assertEqual(updated.error_message, 'Installation failed: network error')

    def test_update_job_status_not_found(self):
        """测试更新不存在的任务"""
        result = DeployService.update_job_status('non-existent', 'running')
        self.assertIsNone(result)
