"""Network LB 扩展功能集成测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models.user import Users
from backend.models.authority import Authority, UserAuthority
from backend.models.network import LoadBalancer


class LBExtensionViewTest(TestCase):
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
        LoadBalancer.objects.create(
            name="lb1", vip_address="10.0.0.1", port=80,
            algorithm="round_robin", status="active"
        )

    def test_by_project_missing_param(self):
        url = reverse("lb-by-project")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 400)

    def test_by_project_success(self):
        url = reverse("lb-by-project")
        response = self.client.get(url, {"project_id": "proj-1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertIn("data", response.data)

    def test_by_k8s_missing_param(self):
        url = reverse("lb-by-k8s")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 400)

    def test_by_k8s_success(self):
        url = reverse("lb-by-k8s")
        response = self.client.get(url, {"k8s_cluster": "k8s-1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertIn("data", response.data)

    def test_az_names(self):
        url = reverse("lb-az-names")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["errno"], 0)
        self.assertIsInstance(response.data["data"], list)
        self.assertGreater(len(response.data["data"]), 0)
