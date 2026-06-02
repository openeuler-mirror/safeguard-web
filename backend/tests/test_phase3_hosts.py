"""Phase 3: Hosts 高级功能测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models.user import Users
from backend.models.host import Host, Cluster
from backend.services.host import HostService
from unittest.mock import patch, MagicMock
import io


class HostServiceAdvancedTest(TestCase):
    def test_generate_random_password(self):
        pwd = HostService.generate_random_password(16)
        self.assertEqual(len(pwd), 16)

    def test_hash_password(self):
        h = HostService.hash_password("test", "key")
        self.assertEqual(len(h), 32)

    def test_batch_update_password(self):
        c = Cluster.objects.create(name="c1")
        h1 = Host.objects.create(hostname="h1", ip_address="1.1.1.1", username="root", password="old", cluster=c)
        h2 = Host.objects.create(hostname="h2", ip_address="1.1.1.2", username="root", password="old", cluster=c)
        result = HostService.batch_update_password([h1.id, h2.id], "newpass123", "key")
        self.assertTrue(result["success"])
        self.assertEqual(result["updated"], 2)
        h1.refresh_from_db()
        self.assertEqual(h1.password, HostService.hash_password("newpass123", "key"))

    def test_batch_update_password_nonexistent(self):
        result = HostService.batch_update_password([99999], "newpass")
        self.assertFalse(result["success"])
        self.assertEqual(result["updated"], 0)

    @patch("backend.services.host.SSHClient")
    def test_remote_command(self, mock_ssh_class):
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.execute_command.return_value = ("stdout", "", 0)
        mock_ssh_class.return_value = mock_client

        c = Cluster.objects.create(name="c1")
        h = Host.objects.create(hostname="h1", ip_address="1.1.1.1", username="root", password="pass", port=22, cluster=c)
        result = HostService.remote_command(h.id, "ls -l")
        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"], "stdout")

    def test_export_hosts_to_excel(self):
        c = Cluster.objects.create(name="c1")
        Host.objects.create(hostname="h1", ip_address="1.1.1.1", username="root", cluster=c)
        data = HostService.export_hosts_to_excel()
        self.assertIsInstance(data, bytes)
        self.assertTrue(len(data) > 0)

    def test_import_hosts_from_excel(self):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["hostname", "ip_address", "port", "username", "status", "os_type", "host_type"])
        ws.append(["h1", "1.1.1.1", 22, "root", "online", "centos", "VMHost"])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        result = HostService.import_hosts_from_excel(buffer)
        self.assertTrue(result["success"])
        self.assertEqual(result["created"], 1)
        self.assertTrue(Host.objects.filter(ip_address="1.1.1.1").exists())


class HostViewAdvancedTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create(
            user="testuser",
            nickname="Test User",
            email="test@example.com",
            enable=1,
        )
        self.user.set_password("testpass123")
        self.user.save()
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.cluster = Cluster.objects.create(name="c1")
        self.host = Host.objects.create(
            hostname="h1", ip_address="1.1.1.1", username="root",
            password="pass", port=22, cluster=self.cluster
        )

    @patch("backend.services.host.HostService.batch_update_password")
    def test_batch_update_password_action(self, mock_batch):
        mock_batch.return_value = {"success": True, "updated": 1, "message": "ok", "password": "new", "failed": []}
        url = reverse("host-batch-update-password")
        response = self.client.post(url, {"host_ids": [self.host.id], "password": "newpass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.host.HostService.remote_command")
    def test_remote_command_action(self, mock_cmd):
        mock_cmd.return_value = {"success": True, "message": "ok", "stdout": "out", "stderr": "", "exit_code": 0}
        url = reverse("host-remote-command", args=[self.host.id])
        response = self.client.post(url, {"command": "ls -l"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
