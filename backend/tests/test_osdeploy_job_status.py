from django.test import TestCase

from backend.models.osdeploy.job_status import JobStatus


class JobStatusModelTest(TestCase):
    """JobStatus 模型测试"""

    def test_create_job_status(self):
        """测试创建任务状态"""
        job = JobStatus.objects.create(
            job_id='JOB-001',
            job_type='os_install',
            target='192.168.1.100',
            status='pending',
            progress=0
        )
        self.assertEqual(job.job_id, 'JOB-001')
        self.assertEqual(job.job_type, 'os_install')
        self.assertEqual(job.target, '192.168.1.100')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)

    def test_job_status_str(self):
        """测试任务状态字符串表示"""
        job = JobStatus(job_id='JOB-002', status='running')
        self.assertEqual(str(job), 'JOB-002 - running')

    def test_job_id_unique(self):
        """测试任务ID唯一性"""
        JobStatus.objects.create(job_id='UNIQUE-001', job_type='os_install', target='target')
        with self.assertRaises(Exception):
            JobStatus.objects.create(job_id='UNIQUE-001', job_type='os_install', target='target')

    def test_job_status_default_values(self):
        """测试任务状态默认值"""
        job = JobStatus.objects.create(
            job_id='DEFAULT-001',
            job_type='os_install',
            target='target'
        )
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress, 0)
        self.assertEqual(job.result, {})
        self.assertEqual(job.error_message, '')

    def test_job_status_all_status_choices(self):
        """测试任务状态所有选项"""
        for status_value, status_label in JobStatus.STATUS_CHOICES:
            job = JobStatus.objects.create(
                job_id=f'JOB-STATUS-{status_value}',
                job_type='os_install',
                target='target',
                status=status_value
            )
            self.assertEqual(job.status, status_value)

    def test_job_status_all_job_type_choices(self):
        """测试任务类型所有选项"""
        for job_type_value, job_type_label in JobStatus.JOB_TYPE_CHOICES:
            job = JobStatus.objects.create(
                job_id=f'JOB-TYPE-{job_type_value}',
                job_type=job_type_value,
                target='target'
            )
            self.assertEqual(job.job_type, job_type_value)

    def test_job_status_with_result(self):
        """测试任务结果JSON字段"""
        result_data = {
            'ip': '192.168.1.100',
            'hostname': 'new-server',
            'installed_packages': ['httpd', 'mysql']
        }
        job = JobStatus.objects.create(
            job_id='JOB-RESULT-001',
            job_type='os_install',
            target='192.168.1.100',
            status='success',
            result=result_data
        )
        self.assertEqual(job.result, result_data)
        self.assertEqual(job.result['ip'], '192.168.1.100')

    def test_job_status_with_error_message(self):
        """测试任务错误信息"""
        job = JobStatus.objects.create(
            job_id='JOB-ERROR-001',
            job_type='os_install',
            target='192.168.1.100',
            status='failed',
            error_message='Network timeout during installation'
        )
        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error_message, 'Network timeout during installation')

    def test_job_status_progress(self):
        """测试任务进度"""
        job = JobStatus.objects.create(
            job_id='JOB-PROGRESS-001',
            job_type='os_install',
            target='192.168.1.100',
            progress=50
        )
        self.assertEqual(job.progress, 50)

        job.progress = 75
        job.save()
        job.refresh_from_db()
        self.assertEqual(job.progress, 75)

    def test_job_status_ordering(self):
        """测试任务按创建时间倒序"""
        job1 = JobStatus.objects.create(
            job_id='JOB-ORDER-001',
            job_type='os_install',
            target='target'
        )
        job2 = JobStatus.objects.create(
            job_id='JOB-ORDER-002',
            job_type='os_install',
            target='target'
        )
        jobs = JobStatus.objects.all()
        # 最新的应该在前面
        self.assertEqual(jobs[0], job2)
        self.assertEqual(jobs[1], job1)