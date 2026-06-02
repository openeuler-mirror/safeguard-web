"""OSmigrate Views 测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.models.user import Users
from backend.models.osmigrate.migrate_job import MigrateJob
from unittest.mock import patch


class MigrateViewSetTest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            user="testuser",
            password="testpass123",
            email="test@example.com",
            nickname="Test",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_migrate_jobs(self):
        MigrateJob.objects.create(
            job_id="migrate-test-001",
            job_type="init",
            target_host="192.168.1.1",
            status="success",
        )
        url = reverse("migrate-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertGreaterEqual(response.data["data"]["count"], 1)

    def test_create_migrate_job(self):
        url = reverse("migrate-list")
        data = {
            "job_id": "migrate-test-002",
            "job_type": "init",
            "target_host": "192.168.1.2",
            "status": "pending",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertTrue(MigrateJob.objects.filter(job_id="migrate-test-002").exists())

    def test_retrieve_migrate_job(self):
        job = MigrateJob.objects.create(
            job_id="migrate-test-003",
            job_type="migrate",
            target_host="192.168.1.3",
            status="running",
        )
        url = reverse("migrate-detail", args=[job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["job_id"], "migrate-test-003")

    @patch("backend.views.osmigrate.migrate.X2cuService.start_migrate_init")
    def test_migrate_init_action(self, mock_init):
        mock_init.return_value = "migrate-init-test"
        url = reverse("migrate-init")
        data = {
            "host": "192.168.1.1",
            "port": "22",
            "username": "root",
            "password": "pass",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertEqual(response.data["data"]["job_id"], "migrate-init-test")
        mock_init.assert_called_once()

    @patch("backend.views.osmigrate.migrate.X2cuService.start_migrate")
    def test_migrate_action(self, mock_migrate):
        mock_migrate.return_value = "migrate-test-job"
        url = reverse("migrate-migrate")
        data = {
            "host": "192.168.1.1",
            "port": "22",
            "username": "root",
            "password": "pass",
            "jobname": "test-job",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        mock_migrate.assert_called_once()

    @patch("backend.views.osmigrate.migrate.X2cuService.start_migrate_back")
    def test_migrate_back_action(self, mock_back):
        mock_back.return_value = "migrate-back-test"
        url = reverse("migrate-back")
        data = {
            "host": "192.168.1.1",
            "port": "22",
            "username": "root",
            "password": "pass",
            "jobname": "test-back",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        mock_back.assert_called_once()

    def test_migrate_status_action(self):
        job = MigrateJob.objects.create(
            job_id="migrate-status-test",
            job_type="migrate",
            target_host="192.168.1.1",
            status="success",
            progress=100,
        )
        url = reverse("migrate-status", args=[job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertEqual(response.data["data"]["status"], "success")
