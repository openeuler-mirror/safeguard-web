"""Security Safeguard 部署视图集成测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models.user import Users
from backend.models.authority import Authority, UserAuthority
from backend.models.security import SafeguardDeploy
from unittest.mock import patch


class SafeguardViewTest(TestCase):
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
        self.admin_auth = Authority.objects.create(authority_id=888, authority_name="超级管理员")
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.sg = SafeguardDeploy.objects.create(
            name="sg1",
            safeguard_type="safeguardx86",
            arch="x86",
            status="pending",
            host="10.0.0.1",
        )

    def test_list_safeguards(self):
        url = reverse("safeguard-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)

    def test_create_safeguard(self):
        url = reverse("safeguard-list")
        data = {
            "name": "sg2",
            "safeguard_type": "safeguardx86",
            "arch": "x86",
            "status": "pending",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.security.SafeguardService.deploy")
    def test_deploy_action(self, mock_deploy):
        mock_deploy.return_value = True
        url = reverse("safeguard-deploy", args=[self.sg.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.security.SafeguardService.rollback")
    def test_rollback_action(self, mock_rollback):
        mock_rollback.return_value = True
        url = reverse("safeguard-rollback", args=[self.sg.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.security.SafeguardService.get_deploy_status")
    def test_status_action(self, mock_status):
        mock_status.return_value = {"status": "running", "progress": 50}
        url = reverse("safeguard-status", args=[self.sg.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertIn("data", response.data)
