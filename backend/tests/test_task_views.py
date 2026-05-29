"""TaskViewSet 单元测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models import Users
from backend.models.task import Task


class TaskViewSetTestCase(TestCase):
    """TaskViewSet API 测试"""

    def setUp(self):
        """测试前置"""
        self.client = APIClient()
        self.user = Users.objects.create(
            user="testuser",
            nickname="Test User",
            email="test@example.com",
            enable=1,
        )
        self.user.set_password("testpassword")
        self.user.save()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # 创建测试数据
        self.task1 = Task.objects.create(
            job_id="job-001",
            job_type="os_install",
            target="host_1",
            status="success",
            progress=100,
        )
        self.task2 = Task.objects.create(
            job_id="job-002",
            job_type="repo_sync",
            target="repo_1",
            status="running",
            progress=50,
        )

    def test_list_tasks(self):
        """测试获取任务列表"""
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["results"]), 2)

    def test_retrieve_task(self):
        """测试获取单个任务详情"""
        response = self.client.get(f"/api/tasks/{self.task1.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["job_id"], "job-001")
        self.assertEqual(data["status"], "success")

    def test_create_task(self):
        """测试创建任务"""
        payload = {
            "job_id": "job-003",
            "job_type": "os_install",
            "target": "host_3",
            "status": "pending",
            "progress": 0,
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["job_id"], "job-003")
        self.assertEqual(Task.objects.count(), 3)

    def test_update_task(self):
        """测试更新任务"""
        payload = {
            "status": "failed",
            "progress": 30,
            "error_message": "network timeout",
        }
        response = self.client.put(
            f"/api/tasks/{self.task1.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["error_message"], "network timeout")

    def test_delete_task(self):
        """测试删除任务"""
        response = self.client.delete(f"/api/tasks/{self.task1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)

    def test_query_action(self):
        """测试 query action"""
        payload = {"job_type": "os_install"}
        response = self.client.post("/api/tasks/query/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["job_type"], "os_install")

    def test_page_action(self):
        """测试 page action"""
        payload = {"status": "running"}
        response = self.client.post("/api/tasks/page/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["status"], "running")

    def test_filter_by_job_type(self):
        """测试按任务类型过滤（通过query action）"""
        payload = {"job_type": "os_install"}
        response = self.client.post("/api/tasks/query/?page=1&page_size=10", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["job_type"], "os_install")

    def test_search_by_target(self):
        """测试按target搜索（通过query action）"""
        payload = {"target": "host_1"}
        response = self.client.post("/api/tasks/query/?page=1&page_size=10", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
