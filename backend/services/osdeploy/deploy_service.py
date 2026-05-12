"""PXE部署服务"""
import uuid
from typing import Optional
from backend.models.osdeploy import JobStatus, KickStartFileStatus, RepoStatus, PXEServerStatus


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
        """启动自动安装任务"""
        # 生成唯一job_id
        job_id = f"install-{uuid.uuid4().hex[:12]}"

        # 获取相关信息
        try:
            kickstart = KickStartFileStatus.objects.get(pk=kickstart_id)
            repo = RepoStatus.objects.get(pk=repo_id)
        except (KickStartFileStatus.DoesNotExist, RepoStatus.DoesNotExist) as e:
            raise ValueError(f"资源不存在: {e}")

        # 创建任务记录
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

        # TODO: 调用实际的装机服务
        # 这里应该触发异步任务执行安装

        return job

    @staticmethod
    def query_job_status(job_id: str) -> Optional[JobStatus]:
        """查询任务状态"""
        try:
            return JobStatus.objects.get(job_id=job_id)
        except JobStatus.DoesNotExist:
            return None

    @staticmethod
    def list_jobs(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取任务列表（支持分页和过滤）"""
        queryset = JobStatus.objects.all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def update_job_status(job_id: str, status: str, progress: int = None, result: dict = None, error_message: str = None) -> Optional[JobStatus]:
        """更新任务状态"""
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
            return job
        except JobStatus.DoesNotExist:
            return None
