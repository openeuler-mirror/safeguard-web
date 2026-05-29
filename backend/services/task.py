"""Task 任务服务"""
import uuid
from typing import Optional
from backend.models.task import Task


class TaskService:
    """任务管理服务"""

    @staticmethod
    def generate_job_id(prefix: str = "job") -> str:
        """生成唯一任务ID"""
        return f"{prefix}-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def create_job(
        job_type: str,
        target: str,
        job_id: str = None,
        status: str = "pending",
        progress: int = 0,
        result: dict = None,
        error_message: str = "",
    ) -> Task:
        """创建任务"""
        if job_id is None:
            job_id = TaskService.generate_job_id(job_type)
        task = Task.objects.create(
            job_id=job_id,
            job_type=job_type,
            target=target,
            status=status,
            progress=progress,
            result=result or {},
            error_message=error_message,
        )
        return task

    @staticmethod
    def update_job(
        job_id: str,
        status: str = None,
        progress: int = None,
        result: dict = None,
        error_message: str = None,
    ) -> Optional[Task]:
        """更新任务状态"""
        try:
            task = Task.objects.get(job_id=job_id)
            if status is not None:
                task.status = status
            if progress is not None:
                task.progress = progress
            if result is not None:
                task.result = result
            if error_message is not None:
                task.error_message = error_message
            task.save()
            return task
        except Task.DoesNotExist:
            return None

    @staticmethod
    def get_job(job_id: str) -> Optional[Task]:
        """根据job_id查询任务"""
        try:
            return Task.objects.get(job_id=job_id)
        except Task.DoesNotExist:
            return None

    @staticmethod
    def get_job_by_id(task_id: int) -> Optional[Task]:
        """根据主键id查询任务"""
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return None

    @staticmethod
    def list_jobs(
        filters: dict = None,
        page: int = 1,
        page_size: int = 10,
    ):
        """分页获取任务列表"""
        queryset = Task.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": results,
        }

    @staticmethod
    def query_by_condition(
        condition: dict = None,
        page: int = 1,
        page_size: int = 10,
    ):
        """按条件查询任务（支持模糊搜索）"""
        queryset = Task.objects.all()
        if condition:
            if condition.get("target"):
                queryset = queryset.filter(target__icontains=condition["target"])
            if condition.get("status"):
                queryset = queryset.filter(status=condition["status"])
            if condition.get("job_type"):
                queryset = queryset.filter(job_type=condition["job_type"])
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": results,
        }

    @staticmethod
    def query_all():
        """查询所有任务"""
        return list(Task.objects.all())

    @staticmethod
    def delete_job(job_id: str) -> bool:
        """删除任务"""
        try:
            task = Task.objects.get(job_id=job_id)
            task.delete()
            return True
        except Task.DoesNotExist:
            return False

    @staticmethod
    def delete_job_by_id(task_id: int) -> bool:
        """根据主键删除任务"""
        try:
            task = Task.objects.get(pk=task_id)
            task.delete()
            return True
        except Task.DoesNotExist:
            return False