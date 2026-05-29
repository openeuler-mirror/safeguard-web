"""TaskService 单元测试"""
from django.test import TestCase
from backend.models.task import Task
from backend.services.task import TaskService


class TaskServiceTestCase(TestCase):
    """TaskService 测试用例"""

    def test_generate_job_id(self):
        """测试生成唯一任务ID"""
        job_id = TaskService.generate_job_id("install")
        self.assertTrue(job_id.startswith("install-"))
        self.assertEqual(len(job_id), len("install-") + 12)

    def test_create_job(self):
        """测试创建任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        self.assertIsNotNone(task.id)
        self.assertEqual(task.job_type, "os_install")
        self.assertEqual(task.target, "host_1")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.progress, 0)
        self.assertTrue(task.job_id.startswith("os_install-"))

    def test_create_job_with_custom_id(self):
        """测试使用自定义job_id创建任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
            job_id="custom-job-001",
        )
        self.assertEqual(task.job_id, "custom-job-001")

    def test_update_job(self):
        """测试更新任务状态"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        updated = TaskService.update_job(
            job_id=task.job_id,
            status="running",
            progress=50,
            result={"step": "downloading"},
            error_message="",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "running")
        self.assertEqual(updated.progress, 50)
        self.assertEqual(updated.result, {"step": "downloading"})

    def test_update_job_not_found(self):
        """测试更新不存在的任务"""
        result = TaskService.update_job(
            job_id="non-existent-job",
            status="running",
        )
        self.assertIsNone(result)

    def test_get_job(self):
        """测试根据job_id查询任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        found = TaskService.get_job(task.job_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, task.id)

    def test_get_job_not_found(self):
        """测试查询不存在的任务"""
        result = TaskService.get_job("non-existent")
        self.assertIsNone(result)

    def test_get_job_by_id(self):
        """测试根据主键id查询任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        found = TaskService.get_job_by_id(task.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.job_id, task.job_id)

    def test_list_jobs(self):
        """测试分页获取任务列表"""
        for i in range(5):
            TaskService.create_job(
                job_type="os_install",
                target=f"host_{i}",
            )
        result = TaskService.list_jobs(page=1, page_size=3)
        self.assertEqual(result["total"], 5)
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["page_size"], 3)

    def test_list_jobs_with_filters(self):
        """测试带过滤条件的任务列表"""
        TaskService.create_job(job_type="os_install", target="host_1")
        TaskService.create_job(job_type="repo_sync", target="repo_1")
        result = TaskService.list_jobs(
            filters={"job_type": "os_install"},
            page=1,
            page_size=10,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0].job_type, "os_install")

    def test_query_by_condition(self):
        """测试按条件查询任务"""
        TaskService.create_job(job_type="os_install", target="host_1")
        TaskService.create_job(job_type="os_install", target="host_2")
        TaskService.create_job(job_type="repo_sync", target="repo_1")
        result = TaskService.query_by_condition(
            condition={"job_type": "os_install", "target": "host_1"},
            page=1,
            page_size=10,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0].target, "host_1")

    def test_query_by_condition_fuzzy_target(self):
        """测试模糊搜索target"""
        TaskService.create_job(job_type="os_install", target="web-server-01")
        TaskService.create_job(job_type="os_install", target="db-server-01")
        result = TaskService.query_by_condition(
            condition={"target": "web"},
            page=1,
            page_size=10,
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0].target, "web-server-01")

    def test_query_all(self):
        """测试查询所有任务"""
        for i in range(3):
            TaskService.create_job(
                job_type="os_install",
                target=f"host_{i}",
            )
        results = TaskService.query_all()
        self.assertEqual(len(results), 3)

    def test_delete_job(self):
        """测试删除任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        success = TaskService.delete_job(task.job_id)
        self.assertTrue(success)
        self.assertIsNone(TaskService.get_job(task.job_id))

    def test_delete_job_not_found(self):
        """测试删除不存在的任务"""
        success = TaskService.delete_job("non-existent")
        self.assertFalse(success)

    def test_delete_job_by_id(self):
        """测试根据主键删除任务"""
        task = TaskService.create_job(
            job_type="os_install",
            target="host_1",
        )
        success = TaskService.delete_job_by_id(task.id)
        self.assertTrue(success)
        self.assertIsNone(TaskService.get_job_by_id(task.id))