"""OSmigrate x2cu Celery 任务"""
import logging
import time

from celery import shared_task

from backend.services.osmigrate.x2cu_service import X2cuService
from backend.models.osmigrate.migrate_job import MigrateJob
from backend.utils.ssh import remote_host_command, local_ping_host

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=0)
def migrate_init_task(self, job_id: str, host: str, port: str, username: str, password: str, hosts, migrate_type: str, redis_passwd: str):
    """异步执行迁移初始化"""
    try:
        X2cuService._update_migrate_job(job_id, status="running", progress=10)

        if not hosts:
            _port = port or "22"
            X2cuService.migrate_init(host, _port, username, password)
            X2cuService._update_migrate_job(job_id, status="success", progress=100, result={"host": host})
        else:
            host_infos = [X2cuService.HostInfo.from_dict(h) for h in hosts]
            if migrate_type == "yunguan":
                if len(host_infos) == 2:
                    h1, h2 = host_infos[0], host_infos[1]
                    X2cuService.migrate_init4_yunguan_portal1(h1.host, h1.port, h1.username, h1.password)
                    X2cuService.migrate_init(h1.host, h1.port, h1.username, h1.password)
                    X2cuService.migrate_init4_yunguan_portal2(h2.host, h2.port, h2.username, h2.password)
                    X2cuService.migrate_init(h2.host, h2.port, h2.username, h2.password)
                elif len(host_infos) == 3:
                    X2cuService.migrate_init4_yunguan_monitor(host_infos[0], host_infos[1], host_infos[2])
                    for h in host_infos:
                        X2cuService.migrate_init(h.host, h.port, h.username, h.password)
                else:
                    raise Exception(f"yunguan node num error: {len(host_infos)}")
            else:
                for h in host_infos:
                    X2cuService.migrate_init(h.host, h.port, h.username, h.password)

            X2cuService._update_migrate_job(job_id, status="success", progress=100, result={"hosts_count": len(host_infos)})
    except Exception as e:
        logger.error(f"Migrate init failed: {e}")
        X2cuService._update_migrate_job(job_id, status="failed", error_message=str(e))
    return {"job_id": job_id, "status": "done"}


@shared_task(bind=True, max_retries=0)
def migrate_task(self, job_id: str, host: str, port: str, username: str, password: str, hosts, migrate_type: str):
    """异步执行迁移"""
    try:
        if not hosts:
            _port = port or "22"
            X2cuService.migrate_core(host, _port, username, password, "")
            X2cuService._update_migrate_job(job_id, status="rebooting", progress=80)

            remote_host_command(host, int(_port), username, password, "reboot")

            for i in range(20):
                res, _ = local_ping_host(host, timeout=5)
                if not res:
                    time.sleep(10)
                    continue
                X2cuService._update_migrate_job(job_id, status="success", progress=100)
                return {"job_id": job_id, "status": "success"}
            X2cuService._update_migrate_job(job_id, status="failed", error_message="ping timeout after reboot")
        else:
            host_infos = [X2cuService.HostInfo.from_dict(h) for h in hosts]
            job_names = []
            for index, h in enumerate(host_infos):
                job_name_tmp = f"{job_id}-{index}"
                job_names.append(job_name_tmp)
                MigrateJob.objects.create(
                    job_id=job_name_tmp,
                    job_type="migrate",
                    target_host=h.host,
                    migrate_type=migrate_type,
                    status="running",
                    progress=0,
                )
                # 直接同步执行单主机迁移（Celery worker 中已是异步）
                _do_single_migrate(h, job_name_tmp)

            # 云管后置处理
            if migrate_type == "yunguan":
                _post_process_yunguan(job_id, job_names, host_infos)
    except Exception as e:
        logger.error(f"Migrate failed: {e}")
        X2cuService._update_migrate_job(job_id, status="failed", error_message=str(e))
    return {"job_id": job_id, "status": "done"}


def _do_single_migrate(h_info, j_name):
    try:
        X2cuService.migrate_core(h_info.host, h_info.port, h_info.username, h_info.password, "")
        X2cuService._update_migrate_job(j_name, status="rebooting", progress=80)
        remote_host_command(h_info.host, int(h_info.port), h_info.username, h_info.password, "reboot")
        for _i in range(20):
            res, _ = local_ping_host(h_info.host, timeout=5)
            if res:
                X2cuService._update_migrate_job(j_name, status="success", progress=100)
                return
            time.sleep(10)
        X2cuService._update_migrate_job(j_name, status="failed", error_message="ping timeout")
    except Exception as e:
        X2cuService._update_migrate_job(j_name, status="failed", error_message=str(e))


def _post_process_yunguan(job_id, job_names, host_infos):
    for _i in range(30):
        all_success = True
        job_fail = False
        for j_name in job_names:
            try:
                j = MigrateJob.objects.get(job_id=j_name)
                if j.status == "failed":
                    job_fail = True
                    break
                elif j.status != "success":
                    all_success = False
                    break
            except MigrateJob.DoesNotExist:
                all_success = False
                break
        if job_fail:
            break
        if all_success:
            if len(host_infos) == 2:
                h1, h2 = host_infos[0], host_infos[1]
                try:
                    X2cuService.migrate_post4_yunguan_portal1(h1.host, h1.port, h1.username, h1.password)
                except Exception as e:
                    X2cuService._update_migrate_job(job_names[0], status="failed", error_message=str(e))
                try:
                    X2cuService.migrate_post4_yunguan_portal1(h2.host, h2.port, h2.username, h2.password)
                except Exception as e:
                    X2cuService._update_migrate_job(job_names[1], status="failed", error_message=str(e))
            elif len(host_infos) == 3:
                try:
                    X2cuService.migrate_post4_yunguan_monitor(host_infos[0], host_infos[1], host_infos[2])
                except Exception as e:
                    X2cuService._update_migrate_job(job_id, status="post fail", error_message=str(e))
            break
        time.sleep(30)


@shared_task(bind=True, max_retries=0)
def migrate_back_task(self, job_id: str, host: str, port: str, username: str, password: str):
    """异步执行迁移回滚"""
    try:
        _port = port or "22"
        X2cuService.migrate_back(host, _port, username, password)
        X2cuService._update_migrate_job(job_id, status="rebooting", progress=80)

        remote_host_command(host, int(_port), username, password, "reboot")

        for i in range(20):
            res, _ = local_ping_host(host, timeout=5)
            if res:
                X2cuService._update_migrate_job(job_id, status="success", progress=100)
                return {"job_id": job_id, "status": "success"}
            time.sleep(10)
        X2cuService._update_migrate_job(job_id, status="failed", error_message="ping timeout after reboot")
    except Exception as e:
        logger.error(f"Migrate back failed: {e}")
        X2cuService._update_migrate_job(job_id, status="failed", error_message=str(e))
    return {"job_id": job_id, "status": "done"}
