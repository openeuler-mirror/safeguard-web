"""
Safeguard 主机安全服务模块

本模块提供主机安全相关的业务服务，包括：
- HostInfoService: 主机信息采集服务（端口、进程、服务等）
- MonitorService: 主机监控数据采集服务（CPU、内存、网络、磁盘等）
- PolicyService: 安全策略管理服务
- AuditService: 操作审计服务
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from django.db import transaction
from django.core.cache import cache

from backend.models.host import Host
from backend.models.safeguard.monitor import HostMonitorData
from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)
from backend.models.safeguard.file_monitor import (
    FileMonitorRule,
    FileMonitorEvent,
)
from backend.models.audit.audit_log import AuditLog
from backend.common.exceptions import (
    HostNotFoundError,
    HostInfoCollectError,
    MonitorDataSaveError,
    MonitorHistoryQueryError,
    MonitorCollectError,
    PolicyTemplateNotFoundError,
    HostPolicyNotFoundError,
    TaskNotFoundError,
    PolicyApplyError,
    AuditLogCreateError,
    FileMonitorRuleCreateError,
    FileMonitorEventCollectError,
    OperationError,
)
from backend.utils.hardware_collector import (
    collect_host_hardware,
    collect_ports,
    collect_processes,
    collect_services,
    collect_cpu_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_disk_metrics,
    collect_system_accounts,
    collect_system_logs,
    control_service,
    get_service_logs,
    kill_process,
    collect_file_events,
)

logger = logging.getLogger(__name__)


class HostInfoService:
    """
    主机信息采集服务

    负责采集主机的端口、进程、服务等信息，
    并提供高风险端口检测、异常进程识别等功能。
    """

    @staticmethod
    def get_system_info(host_id: int) -> Dict[str, Any]:
        """
        获取主机系统基本信息

        Args:
            host_id: 主机ID

        Returns:
            包含系统信息的字典
        """
        try:
            host = Host.objects.get(id=host_id)
            hardware_info = collect_host_hardware(host)
            return hardware_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting system info for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def get_ports_info(host_id: int) -> Dict[str, Any]:
        """
        获取主机端口信息

        Args:
            host_id: 主机ID

        Returns:
            包含端口信息的字典，包括监听端口、连接统计、高风险端口标记
        """
        try:
            host = Host.objects.get(id=host_id)
            port_info = collect_ports(host)
            return port_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting ports info for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def get_processes_info(host_id: int) -> Dict[str, Any]:
        """
        获取主机进程信息

        Args:
            host_id: 主机ID

        Returns:
            包含进程信息的字典，包括进程列表、进程树、高资源占用进程
        """
        try:
            host = Host.objects.get(id=host_id)
            process_info = collect_processes(host)
            return process_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting processes info for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def get_services_info(host_id: int) -> Dict[str, Any]:
        """
        获取主机服务信息

        Args:
            host_id: 主机ID

        Returns:
            包含服务信息的字典
        """
        try:
            host = Host.objects.get(id=host_id)
            service_info = collect_services(host)
            return service_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting services info for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def collect_and_save_ports(host_id: int) -> Dict[str, Any]:
        """
        采集并保存主机端口信息

        Args:
            host_id: 主机ID

        Returns:
            采集结果
        """
        try:
            host = Host.objects.get(id=host_id)
            port_info = collect_ports(host)

            # 使用缓存保存结果（暂时）
            cache_key = f'safeguard:ports:{host_id}'
            cache.set(cache_key, port_info, 3600)

            return port_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting and saving ports for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def get_accounts_info(host_id: int) -> Dict[str, Any]:
        """
        获取主机系统账户信息

        Args:
            host_id: 主机ID

        Returns:
            包含系统账户信息的字典
        """
        try:
            host = Host.objects.get(id=host_id)
            accounts_info = collect_system_accounts(host)
            return accounts_info
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting accounts info for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def control_service(host_id: int, service_name: str, action: str) -> Dict[str, Any]:
        """
        控制主机服务（启动、停止、重启、重载、启用、禁用）

        Args:
            host_id: 主机ID
            service_name: 服务名称
            action: 操作类型

        Returns:
            操作结果字典
        """
        try:
            # Validate inputs first as a safeguard
            allowed_actions = ['start', 'stop', 'restart', 'reload', 'enable', 'disable']
            if action not in allowed_actions:
                raise OperationError(f"Invalid action: {action}")
            if not service_name or not all(c.isalnum() or c in '-_.' for c in service_name):
                raise OperationError(f"Invalid service name: {service_name}")

            host = Host.objects.get(id=host_id)
            result = control_service(host, service_name, action)
            return result
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except OperationError:
            raise
        except Exception as e:
            logger.error(f'Error controlling service {service_name} for host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def get_service_logs(host_id: int, service_name: str, lines: int = 100) -> Dict[str, Any]:
        """
        获取服务日志

        Args:
            host_id: 主机ID
            service_name: 服务名称
            lines: 获取日志行数

        Returns:
            日志信息字典
        """
        try:
            host = Host.objects.get(id=host_id)
            result = get_service_logs(host, service_name, lines)
            return result
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting service logs for {service_name} on host {host_id}: {e}')
            raise HostInfoCollectError(str(e))

    @staticmethod
    def kill_process(host_id: int, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        终止主机上的进程

        Args:
            host_id: 主机ID
            pid: 进程ID
            force: 是否强制终止

        Returns:
            操作结果字典
        """
        try:
            # Validate pid is an integer
            if not isinstance(pid, int):
                try:
                    pid = int(pid)
                except (ValueError, TypeError):
                    raise OperationError(f"Invalid pid: {pid}")

            # Protect init process (PID 1)
            if pid == 1:
                raise OperationError("Cannot kill init process (PID 1)")

            host = Host.objects.get(id=host_id)
            result = kill_process(host, pid, force)
            return result
        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except OperationError:
            raise
        except Exception as e:
            logger.error(f'Error killing process {pid} on host {host_id}: {e}')
            raise HostInfoCollectError(str(e))


class MonitorService:
    """
    主机监控数据采集服务

    负责采集主机的CPU、内存、网络、磁盘等监控数据，
    并提供历史数据查询功能。
    """

    @staticmethod
    def collect_cpu_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集CPU监控数据

        Args:
            host_id: 主机ID

        Returns:
            CPU使用率、负载平均值、每核使用率等

        Raises:
            HostNotFoundError: 主机不存在
            MonitorCollectError: 采集失败
        """
        try:
            host = Host.objects.get(id=host_id)
            result = collect_cpu_metrics(host)
            logger.info(f'CPU metrics collected for host {host_id}')
            return result
        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when collecting CPU metrics')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting CPU metrics for host {host_id}: {e}')
            raise MonitorCollectError(str(e))

    @staticmethod
    def collect_memory_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集内存监控数据

        Args:
            host_id: 主机ID

        Returns:
            内存总量、使用量、Swap使用量、使用率等

        Raises:
            HostNotFoundError: 主机不存在
            MonitorCollectError: 采集失败
        """
        try:
            host = Host.objects.get(id=host_id)
            result = collect_memory_metrics(host)
            logger.info(f'Memory metrics collected for host {host_id}')
            return result
        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when collecting memory metrics')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting memory metrics for host {host_id}: {e}')
            raise MonitorCollectError(str(e))

    @staticmethod
    def collect_network_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集网络监控数据

        Args:
            host_id: 主机ID

        Returns:
            网络接口流量、包统计、错误/丢包统计等

        Raises:
            HostNotFoundError: 主机不存在
            MonitorCollectError: 采集失败
        """
        try:
            host = Host.objects.get(id=host_id)
            result = collect_network_metrics(host)
            logger.info(f'Network metrics collected for host {host_id}')
            return result
        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when collecting network metrics')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting network metrics for host {host_id}: {e}')
            raise MonitorCollectError(str(e))

    @staticmethod
    def collect_disk_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集磁盘监控数据

        Args:
            host_id: 主机ID

        Returns:
            磁盘IO统计、分区使用率、IOPS等

        Raises:
            HostNotFoundError: 主机不存在
            MonitorCollectError: 采集失败
        """
        try:
            host = Host.objects.get(id=host_id)
            result = collect_disk_metrics(host)
            logger.info(f'Disk metrics collected for host {host_id}')
            return result
        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when collecting disk metrics')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting disk metrics for host {host_id}: {e}')
            raise MonitorCollectError(str(e))

    @staticmethod
    def collect_all_metrics(host_id: int, save: bool = True) -> Dict[str, Any]:
        """
        采集所有监控数据

        Args:
            host_id: 主机ID
            save: 是否保存到数据库

        Returns:
            所有监控数据
        """
        try:
            host = Host.objects.get(id=host_id)

            result = {
                'cpu': collect_cpu_metrics(host),
                'memory': collect_memory_metrics(host),
                'network': collect_network_metrics(host),
                'disk': collect_disk_metrics(host),
                'collected_at': datetime.now().isoformat(),
                'saved': False,
            }

            # 保存到数据库
            if save:
                MonitorService.save_monitor_data(host_id, result)
                result['saved'] = True

            logger.info(f'Metrics collected for host {host_id}')
            return result

        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when collecting metrics')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting all metrics for host {host_id}: {e}')
            raise MonitorCollectError(str(e))

    @staticmethod
    def save_monitor_data(host_id: int, data: Dict[str, Any]) -> None:
        """
        保存监控数据

        Args:
            host_id: 主机ID
            data: 监控数据

        Raises:
            HostNotFoundError: 主机不存在
            MonitorDataSaveError: 保存失败
        """
        try:
            host = Host.objects.get(id=host_id)

            with transaction.atomic():
                monitor_data = HostMonitorData.objects.create(
                    host=host,
                )

                # 保存 CPU 数据
                if data.get('cpu') and data['cpu'].get('success'):
                    cpu = data['cpu']
                    monitor_data.cpu_usage = cpu.get('cpu_usage', {}).get('usage_percent')
                    monitor_data.load_1m = cpu.get('load_avg', {}).get('load_1min')
                    monitor_data.load_5m = cpu.get('load_avg', {}).get('load_5min')
                    monitor_data.load_15m = cpu.get('load_avg', {}).get('load_15min')

                # 保存内存数据
                if data.get('memory') and data['memory'].get('success'):
                    memory = data['memory']
                    mem = memory.get('memory', {})
                    monitor_data.memory_total = mem.get('mem_total')
                    monitor_data.memory_used = mem.get('mem_used')
                    monitor_data.memory_usage = mem.get('mem_percent')

                # 保存网络数据
                if data.get('network') and data['network'].get('success'):
                    network = data['network']
                    monitor_data.network_in = network.get('total_rx_bytes')
                    monitor_data.network_out = network.get('total_tx_bytes')

                # 保存磁盘数据
                if data.get('disk') and data['disk'].get('success'):
                    disk = data['disk']
                    total_read = sum(d.get('sectors_read', 0) for d in disk.get('disks', []))
                    total_write = sum(d.get('sectors_written', 0) for d in disk.get('disks', []))
                    monitor_data.disk_read = total_read * 512  # 转换为字节
                    monitor_data.disk_write = total_write * 512

                monitor_data.save()

            logger.info(f'Monitor data saved for host {host_id}')

        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when saving monitor data')
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error saving monitor data for host {host_id}: {e}')
            raise MonitorDataSaveError(str(e))

    @staticmethod
    def batch_save_monitor_data(host_ids: List[int], data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量保存监控数据

        Args:
            host_ids: 主机ID列表
            data_list: 监控数据列表

        Returns:
            保存结果
        """
        # 校验两个列表长度一致
        if len(host_ids) != len(data_list):
            error_msg = f'host_ids and data_list length mismatch: {len(host_ids)} != {len(data_list)}'
            logger.error(error_msg)
            raise MonitorDataSaveError(error_msg)

        success_count = 0
        failed_ids = []

        try:
            with transaction.atomic():
                for host_id, data in zip(host_ids, data_list):
                    try:
                        MonitorService.save_monitor_data(host_id, data)
                        success_count += 1
                    except Exception:
                        failed_ids.append(host_id)

            return {
                'success_count': success_count,
                'failed_ids': failed_ids,
            }

        except Exception as e:
            logger.error(f'Error batch saving monitor data: {e}')
            raise MonitorDataSaveError(str(e))

    @staticmethod
    def get_monitor_history(
        host_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metric_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        查询监控历史数据

        Args:
            host_id: 主机ID
            start_time: 开始时间
            end_time: 结束时间
            metric_type: 指标类型
            page: 页码
            page_size: 每页大小

        Returns:
            监控历史数据
        """
        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            # 基础查询
            queryset = HostMonitorData.objects.filter(host_id=host_id)

            # 时间范围过滤
            if start_time:
                queryset = queryset.filter(timestamp__gte=start_time)
            if end_time:
                queryset = queryset.filter(timestamp__lte=end_time)

            # 排序
            queryset = queryset.order_by('-timestamp')

            # 计算总数
            total = queryset.count()

            # 分页
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            # 构建返回数据
            data = []
            for record in queryset:
                item = {
                    'timestamp': record.timestamp.isoformat(),
                    'cpu_usage': record.cpu_usage,
                    'load_1m': record.load_1m,
                    'load_5m': record.load_5m,
                    'load_15m': record.load_15m,
                    'memory_total': record.memory_total,
                    'memory_used': record.memory_used,
                    'memory_usage': record.memory_usage,
                    'network_in': record.network_in,
                    'network_out': record.network_out,
                    'disk_read': record.disk_read,
                    'disk_write': record.disk_write,
                }

                # 根据指标类型过滤返回字段
                if metric_type == 'cpu':
                    item = {k: v for k, v in item.items() if k in ['timestamp', 'cpu_usage', 'load_1m', 'load_5m', 'load_15m']}
                elif metric_type == 'memory':
                    item = {k: v for k, v in item.items() if k in ['timestamp', 'memory_total', 'memory_used', 'memory_usage']}
                elif metric_type == 'network':
                    item = {k: v for k, v in item.items() if k in ['timestamp', 'network_in', 'network_out']}
                elif metric_type == 'disk':
                    item = {k: v for k, v in item.items() if k in ['timestamp', 'disk_read', 'disk_write']}

                data.append(item)

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error getting monitor history for host {host_id}: {e}')
            raise MonitorHistoryQueryError(str(e))


class PolicyService:
    """
    安全策略管理服务

    负责安全策略模板管理、主机策略绑定、策略应用等功能。
    """

    @staticmethod
    def create_policy_template(data: Dict[str, Any], created_by=None) -> Dict[str, Any]:
        """
        创建安全策略模板

        Args:
            data: 策略模板数据
            created_by: 创建者用户

        Returns:
            创建的策略模板
        """
        try:
            with transaction.atomic():
                template = SafeguardPolicyTemplate.objects.create(
                    name=data['name'],
                    description=data.get('description', ''),
                    template_type=data.get('template_type', 'custom'),
                    is_builtin=data.get('is_builtin', False),
                    config=data.get('config', {}),
                    created_by=created_by,
                )

            logger.info(f'Policy template created: {template.name}')
            return {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'template_type': template.template_type,
                'is_builtin': template.is_builtin,
            }

        except Exception as e:
            logger.error(f'Error creating policy template: {e}')
            raise OperationError(str(e))

    @staticmethod
    def list_policy_templates(
        template_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        获取安全策略模板列表

        Args:
            template_type: 模板类型
            page: 页码
            page_size: 每页大小

        Returns:
            策略模板列表
        """
        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            queryset = SafeguardPolicyTemplate.objects.all()

            if template_type:
                queryset = queryset.filter(template_type=template_type)

            total = queryset.count()
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            data = []
            for template in queryset:
                data.append({
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'template_type': template.template_type,
                    'is_builtin': template.is_builtin,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat(),
                })

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error listing policy templates: {e}')
            raise OperationError(str(e))

    @staticmethod
    def get_policy_template(template_id: int) -> Dict[str, Any]:
        """
        获取策略模板详情

        Args:
            template_id: 模板ID

        Returns:
            策略模板详情
        """
        try:
            template = SafeguardPolicyTemplate.objects.get(id=template_id)
            return {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'template_type': template.template_type,
                'is_builtin': template.is_builtin,
                'config': template.config,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
            }

        except SafeguardPolicyTemplate.DoesNotExist:
            raise PolicyTemplateNotFoundError(template_id)
        except Exception as e:
            logger.error(f'Error getting policy template: {e}')
            raise OperationError(str(e))

    @staticmethod
    def bind_host_policy(host_id: int, template_id: int, created_by=None, created_by_id=None) -> Dict[str, Any]:
        """
        为主机绑定安全策略

        Args:
            host_id: 主机ID
            template_id: 策略模板ID
            created_by: 操作人对象
            created_by_id: 操作人ID

        Returns:
            绑定结果
        """
        try:
            host = Host.objects.get(id=host_id)
            template = SafeguardPolicyTemplate.objects.get(id=template_id)

            with transaction.atomic():
                # 获取或创建主机策略
                policy, created = HostSafeguardPolicy.objects.get_or_create(
                    host=host,
                    defaults={
                        'template': template,
                        'config': template.config.copy(),
                    },
                )

                # 如果已存在，更新策略
                if not created:
                    policy.template = template
                    policy.config = template.config.copy()
                    policy.config_version += 1
                    policy.status = 'pending'
                    policy.save()

                # 创建下发任务
                task_kwargs = {
                    'host': host,
                    'policy': policy,
                    'task_type': 'apply',
                    'status': 'pending',
                }
                if created_by:
                    task_kwargs['created_by'] = created_by
                elif created_by_id:
                    task_kwargs['created_by_id'] = created_by_id
                task = PolicyApplyTask.objects.create(**task_kwargs)

            logger.info(f'Policy bound to host {host_id}: template {template_id}')
            return {
                'policy_id': policy.id,
                'task_id': task.id,
                'host_id': host_id,
                'template_id': template_id,
                'status': policy.status,
            }

        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except SafeguardPolicyTemplate.DoesNotExist:
            raise PolicyTemplateNotFoundError(template_id)
        except Exception as e:
            logger.error(f'Error binding host policy: {e}')
            raise OperationError(str(e))

    @staticmethod
    def get_host_policy(host_id: int) -> Dict[str, Any]:
        """
        获取主机策略

        Args:
            host_id: 主机ID

        Returns:
            主机策略详情
        """
        try:
            policy = HostSafeguardPolicy.objects.select_related('template', 'host').get(host_id=host_id)
            return {
                'id': policy.id,
                'host_id': policy.host_id,
                'host_name': policy.host.hostname,
                'template_id': policy.template_id,
                'template_name': policy.template.name if policy.template else None,
                'config': policy.config,
                'config_version': policy.config_version,
                'status': policy.status,
                'applied_at': policy.applied_at.isoformat() if policy.applied_at else None,
                'last_sync': policy.last_sync.isoformat() if policy.last_sync else None,
            }

        except HostSafeguardPolicy.DoesNotExist:
            raise HostPolicyNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error getting host policy: {e}')
            raise OperationError(str(e))

    @staticmethod
    def apply_policy(task_id: int) -> Dict[str, Any]:
        """
        执行策略下发任务

        Args:
            task_id: 任务ID

        Returns:
            执行结果
        """
        from backend.tasks.safeguard import apply_policy_task

        try:
            # 获取任务对象
            task = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').get(id=task_id)

            # 触发异步任务
            apply_policy_task.delay(task_id)

            return {
                'message': 'Policy apply task has been queued',
                'task_id': task_id,
            }

        except PolicyApplyTask.DoesNotExist:
            raise TaskNotFoundError(task_id)
        except Exception as e:
            logger.error(f'Error applying policy: {e}')
            raise PolicyApplyError(str(e))

    @staticmethod
    def get_task_status(task_id: int) -> Dict[str, Any]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态详情
        """
        try:
            task = PolicyApplyTask.objects.select_related('host', 'policy', 'created_by').get(id=task_id)

            return {
                'id': task.id,
                'host_id': task.host_id,
                'policy_id': task.policy_id,
                'task_type': task.task_type,
                'status': task.status,
                'message': task.message,
                'created_by': task.created_by.user if task.created_by else None,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'finished_at': task.finished_at.isoformat() if task.finished_at else None,
            }

        except PolicyApplyTask.DoesNotExist:
            raise TaskNotFoundError(task_id)
        except Exception as e:
            logger.error(f'Error getting task status: {e}')
            raise OperationError(str(e))


class AuditService:
    """
    操作审计服务

    负责记录用户操作日志、文件监控事件、系统日志等。
    """

    @staticmethod
    def log_action(
        user=None,
        action: str = '',
        resource_type: str = '',
        resource_id: str = '',
        resource_name: str = '',
        action_details: Optional[Dict] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = 'success',
        error_message: str = '',
    ) -> Dict[str, Any]:
        """
        记录操作日志

        Args:
            user: 用户对象
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            action_details: 操作详情
            old_value: 变更前值
            new_value: 变更后值
            ip_address: 客户端IP
            user_agent: User-Agent
            status: 状态
            error_message: 错误消息

        Returns:
            记录结果
        """
        try:
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                action_details=action_details or {},
                old_value=old_value or {},
                new_value=new_value or {},
                ip_address=ip_address,
                user_agent=user_agent or '',
                status=status,
                error_message=error_message,
            )

            logger.info(f'Audit log created: {action} - {resource_name}')
            return {
                'id': audit_log.id,
                'action': audit_log.action,
            }

        except Exception as e:
            logger.error(f'Error logging audit action: {e}')
            raise AuditLogCreateError(str(e))

    @staticmethod
    def list_audit_logs(
        user=None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        获取审计日志列表

        Args:
            user: 过滤用户
            action: 过滤操作类型
            resource_type: 过滤资源类型
            start_time: 开始时间
            end_time: 结束时间
            status: 过滤状态
            page: 页码
            page_size: 每页大小

        Returns:
            审计日志列表
        """
        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            queryset = AuditLog.objects.all()

            if user:
                queryset = queryset.filter(user=user)
            if action:
                queryset = queryset.filter(action=action)
            if resource_type:
                queryset = queryset.filter(resource_type=resource_type)
            if start_time:
                queryset = queryset.filter(created_at__gte=start_time)
            if end_time:
                queryset = queryset.filter(created_at__lte=end_time)
            if status:
                queryset = queryset.filter(status=status)

            total = queryset.count()
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            data = []
            for log in queryset:
                data.append({
                    'id': log.id,
                    'user_id': log.user_id,
                    'user_name': log.user.user if log.user else None,
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'resource_name': log.resource_name,
                    'action_details': log.action_details,
                    'status': log.status,
                    'error_message': log.error_message,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at.isoformat(),
                })

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error listing audit logs: {e}')
            raise OperationError(str(e))

    @staticmethod
    def create_file_monitor_rule(
        host_id: int,
        path: str,
        monitor_type: str = 'file',
        watch_create: bool = True,
        watch_modify: bool = True,
        watch_delete: bool = True,
        watch_access: bool = False,
        watch_perm: bool = True,
        recursive: bool = False,
        includes: Optional[List] = None,
        excludes: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        创建文件监控规则

        Args:
            host_id: 主机ID
            path: 监控路径
            monitor_type: 监控类型
            watch_create: 监控创建事件
            watch_modify: 监控修改事件
            watch_delete: 监控删除事件
            watch_access: 监控访问事件
            watch_perm: 监控权限变更事件
            recursive: 是否递归监控
            includes: 包含规则
            excludes: 排除规则

        Returns:
            创建结果
        """
        try:
            host = Host.objects.get(id=host_id)

            rule = FileMonitorRule.objects.create(
                host=host,
                path=path,
                monitor_type=monitor_type,
                watch_create=watch_create,
                watch_modify=watch_modify,
                watch_delete=watch_delete,
                watch_access=watch_access,
                watch_perm=watch_perm,
                recursive=recursive,
                includes=includes or [],
                excludes=excludes or [],
            )

            logger.info(f'File monitor rule created: {host.hostname} - {path}')
            return {
                'id': rule.id,
                'host_id': host_id,
                'path': path,
                'enabled': rule.enabled,
            }

        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error creating file monitor rule: {e}')
            raise FileMonitorRuleCreateError(str(e))

    @staticmethod
    def list_file_monitor_rules(
        host_id: Optional[int] = None,
        enabled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        获取文件监控规则列表

        Args:
            host_id: 过滤主机
            enabled: 过滤启用状态
            page: 页码
            page_size: 每页大小

        Returns:
            监控规则列表
        """
        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            queryset = FileMonitorRule.objects.all()

            if host_id:
                queryset = queryset.filter(host_id=host_id)
            if enabled is not None:
                queryset = queryset.filter(enabled=enabled)

            total = queryset.count()
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            data = []
            for rule in queryset:
                data.append({
                    'id': rule.id,
                    'host_id': rule.host_id,
                    'host_name': rule.host.hostname,
                    'path': rule.path,
                    'monitor_type': rule.monitor_type,
                    'watch_create': rule.watch_create,
                    'watch_modify': rule.watch_modify,
                    'watch_delete': rule.watch_delete,
                    'watch_access': rule.watch_access,
                    'watch_perm': rule.watch_perm,
                    'recursive': rule.recursive,
                    'enabled': rule.enabled,
                    'created_at': rule.created_at.isoformat(),
                })

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error listing file monitor rules: {e}')
            raise OperationError(str(e))

    @staticmethod
    def list_file_monitor_events(
        host_id: Optional[int] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        获取文件监控事件列表

        Args:
            host_id: 过滤主机
            event_type: 过滤事件类型
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页大小

        Returns:
            文件监控事件列表
        """
        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            queryset = FileMonitorEvent.objects.all()

            if host_id:
                queryset = queryset.filter(host_id=host_id)
            if event_type:
                queryset = queryset.filter(event_type=event_type)
            if start_time:
                queryset = queryset.filter(timestamp__gte=start_time)
            if end_time:
                queryset = queryset.filter(timestamp__lte=end_time)

            total = queryset.count()
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            data = []
            for event in queryset:
                data.append({
                    'id': event.id,
                    'host_id': event.host_id,
                    'host_name': event.host.hostname,
                    'rule_id': event.rule_id,
                    'event_type': event.event_type,
                    'path': event.path,
                    'process_name': event.process_name,
                    'process_id': event.process_id,
                    'user': event.user,
                    'timestamp': event.timestamp.isoformat(),
                    'details': event.details,
                })

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error listing file monitor events: {e}')
            raise OperationError(str(e))

    @staticmethod
    def collect_and_save_system_logs(
        host_id: int,
        log_sources: Optional[List[str]] = None,
        num_lines: int = 100,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        采集并保存系统日志

        Args:
            host_id: 主机ID
            log_sources: 日志源列表
            num_lines: 每个源采集的行数
            save_to_db: 是否保存到数据库

        Returns:
            采集结果数据
        """
        from backend.common.exceptions import HostNotFoundError, OperationError
        try:
            host = Host.objects.get(id=host_id)

            # 采集系统日志
            logs_result = collect_system_logs(host, log_sources, num_lines)

            if logs_result.get('success', False) and save_to_db:
                from backend.models.audit.system_log import SystemLog

                # 保存日志到数据库
                with transaction.atomic():
                    for log_data in logs_result.get('logs', []):
                        # 尝试解析日志的原始时间戳
                        log_timestamp = datetime.now()
                        timestamp_str = log_data.get('timestamp')
                        if timestamp_str:
                            try:
                                # 解析 "Mar 25 14:30:00" 格式的时间
                                parsed = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
                                # 补充年份，默认为当前年份
                                parsed = parsed.replace(year=datetime.now().year)
                                # 如果解析后的时间在未来，说明是去年的日志
                                if parsed > datetime.now():
                                    parsed = parsed.replace(year=datetime.now().year - 1)
                                log_timestamp = parsed
                            except (ValueError, TypeError):
                                # 解析失败，使用当前时间
                                pass

                        SystemLog.objects.create(
                            host=host,
                            source=log_data.get('source', ''),
                            level=log_data.get('level', 'info'),
                            message=log_data.get('message', ''),
                            timestamp=log_timestamp,
                            raw_log=log_data.get('raw_line', ''),
                            parsed_fields={
                                'process': log_data.get('process'),
                                'pid': log_data.get('pid'),
                                'hostname': log_data.get('hostname'),
                            }
                        )

            # 返回数据部分，移除 success 字段
            if 'success' in logs_result:
                logs_result = {k: v for k, v in logs_result.items() if k != 'success'}
            return logs_result

        except Host.DoesNotExist:
            raise HostNotFoundError(host_id)
        except Exception as e:
            logger.error(f'Error collecting system logs for host {host_id}: {e}')
            raise OperationError(str(e))

    @staticmethod
    def get_system_logs(
        host_id: Optional[int] = None,
        source: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        获取系统日志列表

        Args:
            host_id: 过滤主机
            source: 过滤日志源
            level: 过滤日志级别
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页大小

        Returns:
            系统日志列表
        """
        from backend.models.audit.system_log import SystemLog

        try:
            # 校验并标准化分页参数
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 100
            if page_size > 1000:
                page_size = 1000

            queryset = SystemLog.objects.all()

            if host_id:
                queryset = queryset.filter(host_id=host_id)
            if source:
                queryset = queryset.filter(source=source)
            if level:
                queryset = queryset.filter(level=level)
            if start_time:
                queryset = queryset.filter(timestamp__gte=start_time)
            if end_time:
                queryset = queryset.filter(timestamp__lte=end_time)

            # 排序
            queryset = queryset.order_by('-timestamp')

            # 计算总数
            total = queryset.count()

            # 分页
            offset = (page - 1) * page_size
            queryset = queryset[offset:offset + page_size]

            # 构建返回数据
            data = []
            for log in queryset:
                data.append({
                    'id': log.id,
                    'host_id': log.host_id,
                    'host_name': log.host.hostname if log.host else None,
                    'source': log.source,
                    'level': log.level,
                    'message': log.message,
                    'timestamp': log.timestamp.isoformat(),
                    'raw_log': log.raw_log,
                    'parsed_fields': log.parsed_fields,
                    'collected_at': log.collected_at.isoformat(),
                })

            return {
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error getting system logs: {e}')
            raise OperationError(str(e))

    @staticmethod
    def collect_file_events(host_id: Optional[int] = None) -> Dict[str, Any]:
        """
        收集文件监控事件

        Args:
            host_id: 主机ID（可选）

        Returns:
            文件监控事件结果
        """
        try:
            # 获取监控规则
            query = FileMonitorRule.objects.filter(enabled=True)
            if host_id:
                query = query.filter(host_id=host_id)

            rules = list(query.values('id', 'host_id', 'path', 'monitor_type',
                                      'watch_create', 'watch_modify', 'watch_delete',
                                      'watch_access', 'watch_perm', 'recursive'))

            if not rules:
                return {
                    'message': 'No active monitor rules found',
                    'events': [],
                    'total_events': 0,
                }

            # 按主机分组规则
            from collections import defaultdict
            rules_by_host = defaultdict(list)
            for rule in rules:
                rules_by_host[rule['host_id']].append(rule)

            # 收集每个主机的事件
            all_events = []
            for h_id, host_rules in rules_by_host.items():
                try:
                    host = Host.objects.get(id=h_id)
                    result = collect_file_events(host, host_rules)
                    if result['success']:
                        all_events.extend(result['events'])
                except Host.DoesNotExist:
                    continue

            # 保存事件到数据库
            saved_count = AuditService.save_file_events(all_events)

            return {
                'events': all_events,
                'total_events': len(all_events),
                'saved_count': saved_count,
            }

        except Exception as e:
            logger.error(f'Error collecting file events: {e}')
            raise FileMonitorEventCollectError(str(e))

    @staticmethod
    def save_file_events(events: List[Dict[str, Any]]) -> int:
        """
        保存文件监控事件到数据库

        Args:
            events: 文件事件列表

        Returns:
            保存的事件数量
        """
        from django.utils import timezone
        from django.utils.dateparse import parse_datetime
        from backend.models.safeguard.file_monitor import FileMonitorEvent

        def parse_event_timestamp(event: Dict[str, Any]):
            """解析事件中的时间戳，如果解析失败则使用当前时间"""
            timestamp_str = event.get('timestamp')
            if timestamp_str:
                try:
                    parsed = parse_datetime(timestamp_str)
                    if parsed:
                        # 如果是 naive datetime，添加 timezone
                        if timezone.is_naive(parsed):
                            return timezone.make_aware(parsed)
                        return parsed
                except (ValueError, TypeError):
                    pass
            # 解析失败或没有时间戳时，使用当前时间
            return timezone.now()

        saved_count = 0
        try:
            for event in events:
                try:
                    rule_id = event.get('rule_id')
                    if rule_id:
                        # 查找对应的规则
                        rule = FileMonitorRule.objects.filter(id=rule_id).first()
                        if rule:
                            FileMonitorEvent.objects.create(
                                host=rule.host,
                                rule=rule,
                                event_type=event.get('event_type', 'unknown'),
                                path=event.get('path', ''),
                                details=event.get('details', {}),
                                timestamp=parse_event_timestamp(event),
                            )
                            saved_count += 1
                except Exception as e:
                    logger.error(f'Error saving file event: {e}')
                    continue

            logger.info(f'Saved {saved_count} file monitor events')

        except Exception as e:
            logger.error(f'Error saving file events: {e}')

        return saved_count
