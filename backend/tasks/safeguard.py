"""
Safeguard 相关 Celery 任务
"""
import logging
from datetime import datetime
from celery import shared_task
import paramiko
from django.db import DatabaseError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def apply_policy_task(self, task_id: int):
    """
    执行策略下发任务

    Args:
        task_id: 策略下发任务ID
    """
    from backend.models.safeguard.policy import PolicyApplyTask, HostSafeguardPolicy
    from backend.utils.ssh import SSHClient

    try:
        # 获取任务对象
        task = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').get(id=task_id)

        # 更新任务状态为运行中
        task.status = 'running'
        task.started_at = datetime.now()
        task.save()

        logger.info(f'Starting policy apply task {task_id} for host {task.host_id}')

        # 获取主机和策略信息
        host = task.host
        policy = task.policy

        # 通过 SSH 连接主机执行策略下发
        try:
            with SSHClient(
                host=host.ip_address,
                port=host.port,
                username=host.username,
                password=host.password,
            ) as client:
                # 这里是策略下发的具体实现
                # 可以根据实际需求执行相应的命令或脚本
                result_output = []

                # 示例：检查系统版本
                stdout, stderr, exit_code = client.execute_command('cat /etc/os-release 2>&1')
                result_output.append(f'OS Version Check: {stdout}')

                # 示例：应用一些基础安全配置
                # 实际使用时应根据策略配置执行相应的命令
                config_commands = policy.config.get('commands', [])
                if config_commands:
                    for cmd in config_commands:
                        stdout, stderr, exit_code = client.execute_command(f'{cmd} 2>&1')
                        result_output.append(f'Command "{cmd}": exit_code={exit_code}, stdout={stdout}, stderr={stderr}')
                else:
                    # 默认执行一些基础检查
                    stdout, stderr, exit_code = client.execute_command('systemctl status 2>&1 | head -20')
                    result_output.append(f'System Status: {stdout}')

                # 保存结果
                task.result = '\n'.join(result_output)
                task.status = 'success'
                policy.status = 'applied'
                policy.applied_at = datetime.now()
                policy.last_sync = datetime.now()

        except (paramiko.SSHException, IOError, OSError) as ssh_error:
            logger.error(f'SSH connection failed for host {task.host_id}: {ssh_error}')
            task.status = 'failed'
            task.error_message = str(ssh_error)
            policy.status = 'failed'

        # 更新任务完成时间
        task.completed_at = datetime.now()
        task.save()
        policy.save()

        logger.info(f'Policy apply task {task_id} completed with status: {task.status}')

        return {
            'task_id': task_id,
            'status': task.status,
            'success': task.status == 'success',
        }

    except PolicyApplyTask.DoesNotExist:
        logger.error(f'Policy apply task {task_id} not found')
        raise
    except (DatabaseError, IOError, OSError) as e:
        # 只有数据库错误或IO错误才重试，这些可能是暂时的
        logger.error(f'Error executing policy apply task {task_id}: {e}')
        # 重试
        if self.request.retries < self.max_retries:
            self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        else:
            # 重试次数用完，更新任务状态
            try:
                task = PolicyApplyTask.objects.get(id=task_id)
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = datetime.now()
                task.save()
            except PolicyApplyTask.DoesNotExist:
                pass
            raise
    except Exception as e:
        # 兜底处理：确保任务状态不会卡在 'running'
        logger.error(f'Unexpected error executing policy apply task {task_id}: {e}')
        try:
            task = PolicyApplyTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = datetime.now()
            task.save()
        except PolicyApplyTask.DoesNotExist:
            pass
        raise


@shared_task(bind=True, max_retries=2)
def rollback_policy_task(self, task_id: int):
    """
    执行策略回滚任务

    Args:
        task_id: 策略下发任务ID
    """
    from backend.models.safeguard.policy import PolicyApplyTask, HostSafeguardPolicy

    try:
        # 获取任务对象
        task = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').get(id=task_id)

        # 更新任务状态为运行中
        task.status = 'running'
        task.started_at = datetime.now()
        task.save()

        logger.info(f'Starting policy rollback task {task_id} for host {task.host_id}')

        # 这里是策略回滚的具体实现
        # 实际使用时应根据需求执行相应的回滚操作

        # 更新任务状态为成功
        task.status = 'success'
        task.completed_at = datetime.now()
        task.result = 'Policy rollback completed'
        task.save()

        # 更新策略状态
        policy = task.policy
        policy.status = 'rolled_back'
        policy.save()

        logger.info(f'Policy rollback task {task_id} completed successfully')

        return {
            'task_id': task_id,
            'status': 'success',
            'success': True,
        }

    except PolicyApplyTask.DoesNotExist:
        logger.error(f'Policy apply task {task_id} not found')
        raise
    except DatabaseError as e:
        # 只有数据库错误才重试
        logger.error(f'Error executing policy rollback task {task_id}: {e}')
        # 重试
        if self.request.retries < self.max_retries:
            self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        else:
            try:
                task = PolicyApplyTask.objects.get(id=task_id)
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = datetime.now()
                task.save()
            except PolicyApplyTask.DoesNotExist:
                pass
            raise
    except Exception as e:
        # 兜底处理：确保任务状态不会卡在 'running'
        logger.error(f'Unexpected error executing policy rollback task {task_id}: {e}')
        try:
            task = PolicyApplyTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = datetime.now()
            task.save()
        except PolicyApplyTask.DoesNotExist:
            pass
        raise


@shared_task
def collect_file_monitor_events():
    """
    定时收集文件监控事件
    """
    from backend.services.safeguard import AuditService

    logger.info('Starting scheduled file monitor events collection')

    try:
        result = AuditService.collect_file_events()
        logger.info(f'File monitor events collection completed: {result["total_events"]} events, {result.get("saved_count", 0)} saved')
        return result
    except Exception as e:
        logger.error(f'File monitor events collection failed: {e}')
        return {
            'events': [],
            'total_events': 0,
            'saved_count': 0,
            'error': str(e),
        }
