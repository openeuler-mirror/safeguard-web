"""OSdeploy 自动装机 Celery 任务"""
from celery import shared_task

from backend.views.osdeploy.auto_install import AutoInstallViewSet


@shared_task(bind=True, max_retries=0)
def auto_install_os(self, job_id: str, host_id: int, kickstart_id: int, repo_id: int):
    """异步执行单台主机自动装机"""
    viewset = AutoInstallViewSet()
    viewset._do_auto_install(job_id, host_id, kickstart_id, repo_id)
    return {"job_id": job_id, "status": "done"}
