"""OSmigrate Service 测试"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from backend.services.osmigrate.x2cu_service import X2cuService, HostInfo
from backend.models.osmigrate.migrate_job import MigrateJob


class HostInfoTest(TestCase):
    def test_host_info_creation(self):
        h = HostInfo("192.168.1.1", "22", "root", "pass")
        self.assertEqual(h.host, "192.168.1.1")
        self.assertEqual(h.port, "22")

    def test_host_info_to_dict(self):
        h = HostInfo("192.168.1.1", "22", "root", "pass")
        d = h.to_dict()
        self.assertEqual(d["host"], "192.168.1.1")

    def test_host_info_from_dict(self):
        h = HostInfo.from_dict({"host": "192.168.1.1", "port": "22", "username": "root", "password": "pass"})
        self.assertEqual(h.host, "192.168.1.1")


class X2cuServiceTest(TestCase):
    def test_create_migrate_job(self):
        job_id = X2cuService._create_migrate_job("init", "192.168.1.1")
        self.assertTrue(job_id.startswith("migrate-init-"))
        job = MigrateJob.objects.get(job_id=job_id)
        self.assertEqual(job.status, "pending")
        self.assertEqual(job.target_host, "192.168.1.1")

    def test_update_migrate_job(self):
        job_id = X2cuService._create_migrate_job("init", "192.168.1.1")
        X2cuService._update_migrate_job(job_id, status="running", progress=50, error_message="test error")
        job = MigrateJob.objects.get(job_id=job_id)
        self.assertEqual(job.status, "running")
        self.assertEqual(job.progress, 50)
        self.assertEqual(job.error_message, "test error")

    def test_update_nonexistent_job(self):
        # 不应抛出异常
        X2cuService._update_migrate_job("nonexistent", status="running")

    def test_get_migrate_status(self):
        job_id = X2cuService._create_migrate_job("init", "192.168.1.1")
        X2cuService._update_migrate_job(job_id, status="success", progress=100)
        result = X2cuService.get_migrate_status(job_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["progress"], 100)

    def test_get_migrate_status_nonexistent(self):
        result = X2cuService.get_migrate_status("nonexistent")
        self.assertIsNone(result)

    def test_redis_dir_collect(self):
        text = '1) "dir"\n2) "/var/lib/redis"'
        result = X2cuService._redis_dir_collect(text)
        self.assertEqual(result, "/var/lib/redis")

    def test_redis_dir_collect_empty(self):
        text = '1) "dir"\n2) "/root/deploy/redis"'
        result = X2cuService._redis_dir_collect(text)
        self.assertEqual(result, "")

    def test_redis_dir_collect_multi(self):
        text = '"/data/redis"\n"/data/redis2"'
        with self.assertRaises(Exception) as ctx:
            X2cuService._redis_dir_collect(text)
        self.assertIn("redis dir nums gt 1", str(ctx.exception))

    @patch("backend.services.osmigrate.x2cu_service.remote_ping_host")
    @patch("backend.services.osmigrate.x2cu_service.remote_host_command")
    @patch("backend.services.osmigrate.x2cu_service.remote_package_install")
    def test_migrate_init_online(self, mock_install, mock_cmd, mock_ping):
        mock_ping.return_value = (True, "")
        mock_cmd.side_effect = [
            ("x2cu-1.0", 0),  # rpm -qa | grep x2cu
            ("culinux.tar.gz", 0),  # ls /tmp
        ]
        mock_install.return_value = ("", 0)

        X2cuService.migrate_init("192.168.1.1", "22", "root", "pass")
        mock_install.assert_called_once()

    @patch("backend.services.osmigrate.x2cu_service.remote_host_command")
    def test_migrate_core(self, mock_cmd):
        mock_cmd.return_value = ("", 0)
        X2cuService.migrate_core("192.168.1.1", "22", "root", "pass")
        mock_cmd.assert_called_once()
        args = mock_cmd.call_args
        self.assertIn("x2cu", args[0][4])

    @patch("backend.services.osmigrate.x2cu_service.remote_host_command")
    def test_migrate_back(self, mock_cmd):
        mock_cmd.return_value = ("", 0)
        X2cuService.migrate_back("192.168.1.1", "22", "root", "pass")
        mock_cmd.assert_called_once()
        args = mock_cmd.call_args
        self.assertIn("cu2x", args[0][4])

    @patch("backend.tasks.osmigrate.migrate_init_task")
    def test_start_migrate_init(self, mock_task):
        mock_task.delay = MagicMock()

        job_id = X2cuService.start_migrate_init(
            host="192.168.1.1",
            port="22",
            username="root",
            password="pass",
        )
        self.assertTrue(job_id.startswith("migrate-init-"))
        mock_task.delay.assert_called_once()

    @patch("backend.tasks.osmigrate.migrate_task")
    def test_start_migrate(self, mock_task):
        mock_task.delay = MagicMock()

        job_id = X2cuService.start_migrate(
            job_name="test-job",
            host="192.168.1.1",
            port="22",
            username="root",
            password="pass",
        )
        self.assertEqual(job_id, "test-job")
        mock_task.delay.assert_called_once()

    @patch("backend.tasks.osmigrate.migrate_back_task")
    def test_start_migrate_back(self, mock_task):
        mock_task.delay = MagicMock()

        job_id = X2cuService.start_migrate_back(
            job_name="test-back",
            host="192.168.1.1",
            port="22",
            username="root",
            password="pass",
        )
        self.assertEqual(job_id, "test-back")
        mock_task.delay.assert_called_once()
