"""Security Safeguard 部署/回滚 Celery 任务"""
import logging

from celery import shared_task

from backend.services.security.safeguard_service import SafeguardService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=0)
def deploy_safeguard(self, safeguard_id: int, task_job_id: str):
    """异步执行 Safeguard 部署"""
    SafeguardService._deploy_async(safeguard_id, task_job_id)
    return {"safeguard_id": safeguard_id, "task_job_id": task_job_id, "status": "done"}


@shared_task(bind=True, max_retries=0)
def rollback_safeguard(self, safeguard_id: int, task_job_id: str):
    """异步执行 Safeguard 回滚"""
    SafeguardService._rollback_async(safeguard_id, task_job_id)
    return {"safeguard_id": safeguard_id, "task_job_id": task_job_id, "status": "done"}
