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
from backend.utils.hardware_collector import (
    collect_host_hardware,
    collect_ports,
    collect_processes,
    collect_services,
    collect_cpu_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_disk_metrics,
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
            return {
                'success': True,
                'data': hardware_info,
            }
        except Host.DoesNotExist:
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error getting system info for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error getting ports info for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error getting processes info for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error getting services info for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error collecting and saving ports for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }


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
        """
        try:
            host = Host.objects.get(id=host_id)
            return collect_cpu_metrics(host)
        except Host.DoesNotExist:
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error collecting CPU metrics for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    @staticmethod
    def collect_memory_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集内存监控数据

        Args:
            host_id: 主机ID

        Returns:
            内存总量、使用量、Swap使用量、使用率等
        """
        try:
            host = Host.objects.get(id=host_id)
            return collect_memory_metrics(host)
        except Host.DoesNotExist:
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error collecting memory metrics for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    @staticmethod
    def collect_network_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集网络监控数据

        Args:
            host_id: 主机ID

        Returns:
            网络接口流量、包统计、错误/丢包统计等
        """
        try:
            host = Host.objects.get(id=host_id)
            return collect_network_metrics(host)
        except Host.DoesNotExist:
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error collecting network metrics for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    @staticmethod
    def collect_disk_metrics(host_id: int) -> Dict[str, Any]:
        """
        采集磁盘监控数据

        Args:
            host_id: 主机ID

        Returns:
            磁盘IO统计、分区使用率、IOPS等
        """
        try:
            host = Host.objects.get(id=host_id)
            return collect_disk_metrics(host)
        except Host.DoesNotExist:
            return {
                'success': False,
                'error': f'Host {host_id} not found',
            }
        except Exception as e:
            logger.error(f'Error collecting disk metrics for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
        result = {
            'success': False,
            'cpu': None,
            'memory': None,
            'network': None,
            'disk': None,
            'collected_at': datetime.now().isoformat(),
            'saved': False,
        }

        try:
            host = Host.objects.get(id=host_id)

            result['cpu'] = collect_cpu_metrics(host)
            result['memory'] = collect_memory_metrics(host)
            result['network'] = collect_network_metrics(host)
            result['disk'] = collect_disk_metrics(host)
            result['success'] = True

            # 保存到数据库
            if save:
                saved = MonitorService.save_monitor_data(host_id, result)
                result['saved'] = saved

        except Host.DoesNotExist:
            result['error'] = f'Host {host_id} not found'
        except Exception as e:
            logger.error(f'Error collecting all metrics for host {host_id}: {e}')
            result['error'] = str(e)

        return result

    @staticmethod
    def save_monitor_data(host_id: int, data: Dict[str, Any]) -> bool:
        """
        保存监控数据

        Args:
            host_id: 主机ID
            data: 监控数据

        Returns:
            是否保存成功
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
            return True

        except Host.DoesNotExist:
            logger.error(f'Host {host_id} not found when saving monitor data')
            return False
        except Exception as e:
            logger.error(f'Error saving monitor data for host {host_id}: {e}')
            return False

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
        success_count = 0
        failed_ids = []

        try:
            with transaction.atomic():
                for host_id, data in zip(host_ids, data_list):
                    if MonitorService.save_monitor_data(host_id, data):
                        success_count += 1
                    else:
                        failed_ids.append(host_id)

            return {
                'success': True,
                'success_count': success_count,
                'failed_ids': failed_ids,
            }

        except Exception as e:
            logger.error(f'Error batch saving monitor data: {e}')
            return {
                'success': False,
                'error': str(e),
            }

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
                'success': True,
                'data': data,
                'page': page,
                'page_size': page_size,
                'total': total,
            }

        except Exception as e:
            logger.error(f'Error getting monitor history for host {host_id}: {e}')
            return {
                'success': False,
                'error': str(e),
            }


class PolicyService:
    """
    安全策略管理服务

    负责安全策略模板管理、主机策略绑定、策略应用等功能。
    """

    @staticmethod
    def create_policy_template(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建安全策略模板

        Args:
            data: 策略模板数据

        Returns:
            创建的策略模板
        """
        pass

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
        pass

    @staticmethod
    def bind_host_policy(host_id: int, template_id: int) -> Dict[str, Any]:
        """
        为主机绑定安全策略

        Args:
            host_id: 主机ID
            template_id: 策略模板ID

        Returns:
            绑定结果
        """
        pass


class AuditService:
    """
    操作审计服务

    负责记录用户操作日志、文件监控事件、系统日志等。
    """
    pass
