"""PXE部署服务"""
import uuid
from typing import Optional
from backend.models.osdeploy import JobStatus, KickStartFileStatus, RepoStatus, PXEServerStatus
from backend.services.task import TaskService


class DeployService:
    """PXE部署服务"""

    @staticmethod
    def create_pxe_config(host_id: int, kickstart_id: int) -> dict:
        """创建PXE配置"""
        # TODO: 实现PXE配置生成逻辑
        pass

    @staticmethod
    def generate_kickstart(template_id: int, vars: dict) -> str:
        """生成Kickstart文件内容"""
        try:
            template = KickStartFileStatus.objects.get(pk=template_id)
            content = template.content
            # 简单的变量替换
            for key, value in vars.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            return content
        except KickStartFileStatus.DoesNotExist:
            raise ValueError(f"Kickstart模板不存在: {template_id}")

    @staticmethod
    def start_auto_install(host_id: int, kickstart_id: int, repo_id: int) -> JobStatus:
        """启动自动安装任务（保持JobStatus兼容，同时创建Task）"""
        # 获取相关信息
        try:
            kickstart = KickStartFileStatus.objects.get(pk=kickstart_id)
            repo = RepoStatus.objects.get(pk=repo_id)
        except (KickStartFileStatus.DoesNotExist, RepoStatus.DoesNotExist) as e:
            raise ValueError(f"资源不存在: {e}")

        job_id = f"install-{uuid.uuid4().hex[:12]}"

        # 创建 JobStatus 保持兼容
        job = JobStatus.objects.create(
            job_id=job_id,
            job_type="os_install",
            target=f"host_{host_id}",
            status="pending",
            progress=0,
            result={
                "host_id": host_id,
                "kickstart_id": kickstart_id,
                "repo_id": repo_id,
                "kickstart_name": kickstart.name,
                "repo_name": repo.name,
            }
        )

        # 同时创建 Task 用于新追踪
        TaskService.create_job(
            job_type="os_install",
            target=f"host_{host_id}",
            job_id=job_id,
            status="pending",
            progress=0,
            result={
                "host_id": host_id,
                "kickstart_id": kickstart_id,
                "repo_id": repo_id,
                "kickstart_name": kickstart.name,
                "repo_name": repo.name,
            }
        )

        # TODO: 调用实际的装机服务
        # 这里应该触发异步任务执行安装

        return job

    @staticmethod
    def query_job_status(job_id: str) -> Optional[JobStatus]:
        """查询任务状态（兼容旧接口，优先查询 Task，回退到 JobStatus）"""
        from backend.models.task import Task
        try:
            return Task.objects.get(job_id=job_id)
        except Task.DoesNotExist:
            try:
                return JobStatus.objects.get(job_id=job_id)
            except JobStatus.DoesNotExist:
                return None

    @staticmethod
    def list_jobs(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取任务列表（支持分页和过滤，同时查询 JobStatus 和 Task）"""
        from backend.models.task import Task
        # 合并 JobStatus 和 Task 的查询结果
        jobstatus_qs = JobStatus.objects.all()
        task_qs = Task.objects.all()
        if filters:
            jobstatus_qs = jobstatus_qs.filter(**filters)
            task_qs = task_qs.filter(**filters)

        # 合并结果（去重：优先 Task）
        task_job_ids = set(task_qs.values_list('job_id', flat=True))
        jobstatus_results = [j for j in jobstatus_qs if j.job_id not in task_job_ids]
        results = list(task_qs) + jobstatus_results
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results[start:end]
        }

    @staticmethod
    def update_job_status(job_id: str, status: str, progress: int = None, result: dict = None, error_message: str = None):
        """更新任务状态（同时更新 Task 和 JobStatus）"""
        # 优先更新 Task
        updated = TaskService.update_job(
            job_id=job_id,
            status=status,
            progress=progress,
            result=result,
            error_message=error_message,
        )
        # 同时更新 JobStatus 保持兼容
        try:
            job = JobStatus.objects.get(job_id=job_id)
            job.status = status
            if progress is not None:
                job.progress = progress
            if result is not None:
                job.result = result
            if error_message is not None:
                job.error_message = error_message
            job.save()
            if updated is None:
                updated = job
        except JobStatus.DoesNotExist:
            pass
        return updated
