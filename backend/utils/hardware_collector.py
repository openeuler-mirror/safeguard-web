"""
硬件信息采集工具

通过 SSH 连接到远程主机，采集硬件信息（CPU、内存、磁盘、网络等）
"""
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from backend.models.host import Host
from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)

# 高风险端口列表
HIGH_RISK_PORTS = {
    21,    # FTP
    22,    # SSH (管理端口，需要特别关注)
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    111,   # RPC
    135,   # MS RPC
    139,   # NetBIOS
    445,   # SMB
    3306,  # MySQL
    3389,  # RDP
    5432,  # PostgreSQL
    6379,  # Redis
    27017, # MongoDB
    9200,  # Elasticsearch
}


def _get_listening_ports(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取监听端口列表

    Args:
        client: SSH 客户端

    Returns:
        监听端口列表，每个元素包含端口、协议、进程名等
    """
    ports = []
    try:
        # 使用 ss 命令获取监听端口
        stdout, stderr, exit_code = client.execute_command(
            "ss -tuln -p 2>/dev/null || netstat -tuln -p 2>/dev/null"
        )
        if exit_code != 0 or not stdout:
            logger.warning("Failed to get listening ports")
            return ports

        # 解析 ss/netstat 输出
        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith(('State', 'Proto', 'Active')):
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            # 尝试提取协议和地址
            proto = parts[0].lower() if parts[0].lower() in ('tcp', 'udp') else 'tcp'

            # 提取本地地址
            local_addr = parts[3] if 'LISTEN' in parts or '0.0.0.0:*' in parts[4] else parts[3]
            if ':' in local_addr:
                # IPv4:port 格式
                port_part = local_addr.rsplit(':', 1)[-1]
            else:
                port_part = local_addr

            try:
                port = int(port_part)
            except (ValueError, IndexError):
                continue

            # 提取进程信息
            process_name = ''
            pid = ''
            if len(parts) >= 7:
                process_part = ' '.join(parts[6:])
                # 匹配类似 "pid=1234,process=sshd" 的格式
                pid_match = re.search(r'pid=(\d+)', process_part)
                proc_match = re.search(r'process=([^\s,]+)', process_part)
                if pid_match:
                    pid = pid_match.group(1)
                if proc_match:
                    process_name = proc_match.group(1)

            ports.append({
                'port': port,
                'protocol': proto,
                'process_name': process_name,
                'pid': pid,
                'is_high_risk': port in HIGH_RISK_PORTS
            })

    except Exception as e:
        logger.error(f"Error getting listening ports: {e}")

    return ports


def _get_connection_stats(client: SSHClient) -> Dict[str, int]:
    """
    获取连接统计信息

    Args:
        client: SSH 客户端

    Returns:
        各状态的连接数统计
    """
    stats = {
        'ESTABLISHED': 0,
        'TIME_WAIT': 0,
        'LISTEN': 0,
        'CLOSE_WAIT': 0,
        'FIN_WAIT1': 0,
        'FIN_WAIT2': 0,
        'SYN_SENT': 0,
        'SYN_RECV': 0,
        'LAST_ACK': 0,
        'CLOSING': 0,
    }

    try:
        stdout, stderr, exit_code = client.execute_command(
            "ss -tuan state all 2>/dev/null || netstat -tuan 2>/dev/null"
        )
        if exit_code != 0 or not stdout:
            return stats

        lines = stdout.strip().split('\n')
        for line in lines:
            for state in stats.keys():
                if state in line:
                    stats[state] += 1

    except Exception as e:
        logger.error(f"Error getting connection stats: {e}")

    return stats


def _is_high_risk_port(port: int) -> bool:
    """
    判断端口是否为高风险端口

    Args:
        port: 端口号

    Returns:
        是否为高风险端口
    """
    return port in HIGH_RISK_PORTS


def collect_ports(host: Host) -> Dict[str, Any]:
    """
    采集主机端口信息

    Args:
        host: Host 模型实例

    Returns:
        {
            'listening_ports': [...],      # 监听端口列表
            'connection_stats': {...},     # 连接统计
            'high_risk_ports': [...],      # 高风险端口列表
            'total_listening': int,        # 监听端口总数
            'total_high_risk': int,        # 高风险端口数
            'collected_at': str,           # 采集时间
        }
    """
    result = {
        'listening_ports': [],
        'connection_stats': {},
        'high_risk_ports': [],
        'total_listening': 0,
        'total_high_risk': 0,
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取监听端口
            listening_ports = _get_listening_ports(client)
            result['listening_ports'] = listening_ports
            result['total_listening'] = len(listening_ports)

            # 获取连接统计
            connection_stats = _get_connection_stats(client)
            result['connection_stats'] = connection_stats

            # 提取高风险端口
            high_risk_ports = [p for p in listening_ports if p['is_high_risk']]
            result['high_risk_ports'] = high_risk_ports
            result['total_high_risk'] = len(high_risk_ports)

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect ports from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def collect_host_hardware(host: Host) -> Dict[str, str]:
    """
    采集主机硬件信息

    通过 SSH 连接到主机，执行以下命令获取信息：
    - uname -r: 内核版本
    - uptime: 运行时间
    - cat /etc/os-release: OS版本
    - lscpu: CPU信息
    - lsblk: 磁盘信息
    - mount: 挂载信息
    - awk '/MemTotal/': 内存信息
    - ip addr: 网络信息
    - dmesg -T: dmesg信息

    Args:
        host: Host 模型实例

    Returns:
        {
            'arch_info': str,      # 内核架构信息
            'uptime': str,         # 运行时间
            'os_version': str,     # 操作系统版本
            'cpu_info': str,       # CPU信息
            'disk_info': str,      # 磁盘信息
            'memory_info': str,    # 内存信息
            'network_info': str,   # 网络信息
            'mount_info': str,     # 挂载信息
            'dmesg_info': str      # dmesg信息
        }
    """
    result = {
        'arch_info': '',
        'uptime': '',
        'os_version': '',
        'cpu_info': '',
        'disk_info': '',
        'memory_info': '',
        'network_info': '',
        'mount_info': '',
        'dmesg_info': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取内核架构信息
            stdout, stderr, _ = client.execute_command('uname -r')
            if stdout:
                result['arch_info'] = stdout.strip()

            # 获取运行时间
            stdout, stderr, _ = client.execute_command('uptime')
            if stdout:
                result['uptime'] = stdout.strip()

            # 获取 OS 版本
            stdout, stderr, _ = client.execute_command('cat /etc/os-release')
            if stdout:
                result['os_version'] = stdout.strip()

            # 获取 CPU 信息
            stdout, stderr, _ = client.execute_command('lscpu')
            if stdout:
                result['cpu_info'] = stdout.strip()

            # 获取磁盘信息
            stdout, stderr, _ = client.execute_command('lsblk')
            if stdout:
                result['disk_info'] = stdout.strip()

            # 获取内存信息
            stdout, stderr, _ = client.execute_command(
                "awk '/MemTotal/ { printf \"%.2f GB\\n\", $2/1024/1024 }' /proc/meminfo"
            )
            if stdout:
                result['memory_info'] = stdout.strip()

            # 获取网络信息
            stdout, stderr, _ = client.execute_command('ip addr')
            if stdout:
                result['network_info'] = stdout.strip()

            # 获取挂载信息
            stdout, stderr, _ = client.execute_command('mount')
            if stdout:
                result['mount_info'] = stdout.strip()

            # 获取 dmesg 信息
            stdout, stderr, _ = client.execute_command('dmesg -T')
            if stdout:
                result['dmesg_info'] = stdout.strip()

    except Exception as e:
        logger.error(f"Failed to collect hardware info from host {host.id}: {e}")

    return result


def collect_host_lldp(host: Host) -> List[Dict[str, str]]:
    """
    采集 LLDP 拓扑信息

    需要目标主机上运行 lldpd 服务

    Args:
        host: Host 模型实例

    Returns:
        [
            {
                'ifname': str,           # 接口名称
                'peer_dev_name': str,    # 对端设备名
                'peer_chassis_type': str,# 对端设备类型
                'peer_chassis_value': str,# 对端设备标识
                'peer_port_id': str,     # 对端端口ID
                'vlan': str              # VLAN
            },
            ...
        ]
    """
    lldp_infos = []

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 执行 lldpctl 命令
            stdout, stderr, exit_code = client.execute_command('lldpctl -f json')
            if exit_code != 0 or not stdout:
                logger.warning(f"lldpctl failed or returned no data for host {host.id}")
                return lldp_infos

            import json
            data = json.loads(stdout)

            # 解析 lldpctl 输出
            # 格式: {"lldp": {"interface": [{"chassis": {...}, "port": {...}}, ...]}}
            lldp_data = data.get('lldp', {})
            interfaces = lldp_data.get('interface', [])

            for iface in interfaces:
                iface_name = iface.get('name', '')
                chassis = iface.get('chassis', {})
                port = iface.get('port', {})

                # 提取 chassis 信息
                chassis_info = chassis.get('chassis', {})
                if isinstance(chassis_info, list):
                    chassis_info = chassis_info[0] if chassis_info else {}

                # 提取 port 信息
                port_info = port.get('port', {})
                if isinstance(port_info, list):
                    port_info = port_info[0] if port_info else {}

                # 构建 LLDP 条目
                entry = {
                    'ifname': iface_name,
                    'peer_dev_name': chassis_info.get('name', ''),
                    'peer_chassis_type': chassis_info.get('type', ''),
                    'peer_chassis_value': chassis_info.get('id', {}).get('value', ''),
                    'peer_port_id': port_info.get('id', {}).get('value', ''),
                    'vlan': str(port_info.get('vlan', '')),
                }
                lldp_infos.append(entry)

    except Exception as e:
        logger.error(f"Failed to collect LLDP info from host {host.id}: {e}")

    return lldp_infos


def update_host_hardware_info(host: Host) -> bool:
    """
    更新主机的硬件信息

    采集硬件信息并更新到数据库

    Args:
        host: Host 模型实例

    Returns:
        是否更新成功
    """
    try:
        hardware_info = collect_host_hardware(host)

        host.arch_info = hardware_info.get('arch_info', '')
        host.uptime = hardware_info.get('uptime', '')
        host.os_version = hardware_info.get('os_version', '')
        host.cpu_info = hardware_info.get('cpu_info', '')
        host.disk_info = hardware_info.get('disk_info', '')
        host.memory_info = hardware_info.get('memory_info', '')
        host.network_info = hardware_info.get('network_info', '')
        host.mount_info = hardware_info.get('mount_info', '')
        host.dmesg_info = hardware_info.get('dmesg_info', '')
        host.save()
        return True

    except Exception as e:
        logger.error(f"Failed to update hardware info for host {host.id}: {e}")
        return False


def update_host_lldp_info(host: Host) -> bool:
    """
    更新主机的 LLDP 信息

    采集 LLDP 信息并更新到数据库

    Args:
        host: Host 模型实例

    Returns:
        是否更新成功
    """
    try:
        lldp_infos = collect_host_lldp(host)
        host.lldp_infos = lldp_infos
        host.save()
        return True

    except Exception as e:
        logger.error(f"Failed to update LLDP info for host {host.id}: {e}")
        return False


def collect_all_hardware_info(host: Host) -> Dict:
    """
    采集主机的所有硬件信息（包括 LLDP）

    Args:
        host: Host 模型实例

    Returns:
        {
            'hardware': {...},
            'lldp': [...]
        }
    """
    hardware = collect_host_hardware(host)
    lldp = collect_host_lldp(host)

    return {
        'hardware': hardware,
        'lldp': lldp,
    }


def _get_process_list(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取进程列表

    Args:
        client: SSH 客户端

    Returns:
        进程列表
    """
    processes = []
    try:
        # 使用 ps aux 命令获取进程列表
        stdout, stderr, exit_code = client.execute_command(
            "ps aux --no-headers 2>/dev/null || ps -ef 2>/dev/null"
        )
        if exit_code != 0 or not stdout:
            logger.warning("Failed to get process list")
            return processes

        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 10:
                continue

            # 尝试解析 ps aux 输出
            try:
                user = parts[0]
                pid = int(parts[1])
                cpu_percent = float(parts[2]) if parts[2].replace('.', '').isdigit() else 0.0
                mem_percent = float(parts[3]) if parts[3].replace('.', '').isdigit() else 0.0
                vsz = int(parts[4]) if parts[4].isdigit() else 0
                rss = int(parts[5]) if parts[5].isdigit() else 0
                tty = parts[6]
                stat = parts[7]
                start = parts[8]
                time = parts[9]
                command = ' '.join(parts[10:]) if len(parts) > 10 else ''

                processes.append({
                    'pid': pid,
                    'user': user,
                    'cpu_percent': cpu_percent,
                    'mem_percent': mem_percent,
                    'vsz': vsz,
                    'rss': rss,
                    'tty': tty,
                    'stat': stat,
                    'start': start,
                    'time': time,
                    'command': command,
                })
            except (ValueError, IndexError):
                continue

    except Exception as e:
        logger.error(f"Error getting process list: {e}")

    return processes


def _get_process_tree(processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    构建进程树

    Args:
        processes: 进程列表

    Returns:
        进程树
    """
    # 先获取 ppid 信息
    # 这里简化处理，实际可以通过 ps -ef 获取完整父子关系
    return processes


def _detect_high_cpu_processes(
    processes: List[Dict[str, Any]],
    threshold: float = 50.0
) -> List[Dict[str, Any]]:
    """
    检测高CPU占用进程

    Args:
        processes: 进程列表
        threshold: CPU使用率阈值

    Returns:
        高CPU占用进程列表
    """
    return [p for p in processes if p.get('cpu_percent', 0) > threshold]


def _detect_high_memory_processes(
    processes: List[Dict[str, Any]],
    threshold: float = 30.0
) -> List[Dict[str, Any]]:
    """
    检测高内存占用进程

    Args:
        processes: 进程列表
        threshold: 内存使用率阈值

    Returns:
        高内存占用进程列表
    """
    return [p for p in processes if p.get('mem_percent', 0) > threshold]


def collect_processes(host: Host) -> Dict[str, Any]:
    """
    采集主机进程信息

    Args:
        host: Host 模型实例

    Returns:
        {
            'processes': [...],           # 进程列表
            'process_tree': [...],        # 进程树
            'high_cpu_processes': [...],  # 高CPU占用进程
            'high_mem_processes': [...],  # 高内存占用进程
            'total_processes': int,       # 进程总数
            'collected_at': str,          # 采集时间
        }
    """
    result = {
        'processes': [],
        'process_tree': [],
        'high_cpu_processes': [],
        'high_mem_processes': [],
        'total_processes': 0,
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取进程列表
            processes = _get_process_list(client)
            result['processes'] = processes
            result['total_processes'] = len(processes)

            # 构建进程树
            process_tree = _get_process_tree(processes)
            result['process_tree'] = process_tree

            # 检测高CPU进程
            high_cpu = _detect_high_cpu_processes(processes)
            result['high_cpu_processes'] = high_cpu

            # 检测高内存进程
            high_mem = _detect_high_memory_processes(processes)
            result['high_mem_processes'] = high_mem

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect processes from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_systemd_services(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取 systemd 服务列表

    Args:
        client: SSH 客户端

    Returns:
        服务列表
    """
    services = []
    try:
        # 使用 systemctl list-units 命令获取服务列表
        stdout, stderr, exit_code = client.execute_command(
            "systemctl list-units --type=service --all --no-legend 2>/dev/null || echo ''"
        )
        if exit_code != 0 or not stdout:
            # 尝试使用 service 命令
            stdout, stderr, exit_code = client.execute_command(
                "service --status-all 2>/dev/null || echo ''"
            )
            if exit_code != 0 or not stdout:
                return services

        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 解析 systemctl 输出格式: "  sshd.service  loaded  active  running  OpenSSH server"
            parts = line.split(None, 4)
            if len(parts) >= 4:
                service_name = parts[0]
                load_state = parts[1]
                active_state = parts[2]
                sub_state = parts[3]
                description = parts[4] if len(parts) > 4 else ''

                # 去除 .service 后缀
                if service_name.endswith('.service'):
                    service_name = service_name[:-8]

                services.append({
                    'name': service_name,
                    'load_state': load_state,
                    'active_state': active_state,
                    'sub_state': sub_state,
                    'description': description,
                })

    except Exception as e:
        logger.error(f"Error getting systemd services: {e}")

    return services


def _get_service_enabled_status(client: SSHClient, service_name: str) -> str:
    """
    获取服务开机自启状态

    Args:
        client: SSH 客户端
        service_name: 服务名称

    Returns:
        'enabled' | 'disabled' | 'unknown'
    """
    try:
        stdout, stderr, exit_code = client.execute_command(
            f"systemctl is-enabled {service_name} 2>/dev/null"
        )
        if exit_code == 0 and stdout:
            return stdout.strip()
    except Exception as e:
        logger.error(f"Error getting service enabled status for {service_name}: {e}")

    return 'unknown'


def _control_service(client: SSHClient, service_name: str, action: str) -> bool:
    """
    控制服务启停

    Args:
        client: SSH 客户端
        service_name: 服务名称
        action: 'start' | 'stop' | 'restart' | 'reload'

    Returns:
        是否成功
    """
    try:
        stdout, stderr, exit_code = client.execute_command(
            f"systemctl {action} {service_name} 2>&1"
        )
        return exit_code == 0
    except Exception as e:
        logger.error(f"Error {action} service {service_name}: {e}")
        return False


def collect_services(host: Host) -> Dict[str, Any]:
    """
    采集主机服务信息

    Args:
        host: Host 模型实例

    Returns:
        {
            'services': [...],        # 服务列表
            'total_services': int,    # 服务总数
            'running_services': int,  # 运行中的服务数
            'collected_at': str,      # 采集时间
        }
    """
    result = {
        'services': [],
        'total_services': 0,
        'running_services': 0,
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取服务列表
            services = _get_systemd_services(client)
            result['services'] = services
            result['total_services'] = len(services)

            # 统计运行中的服务
            running_services = [
                s for s in services
                if s.get('active_state') in ('active', 'running')
            ]
            result['running_services'] = len(running_services)

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect services from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_cpu_usage_from_proc(client: SSHClient) -> Dict[str, Any]:
    """
    从 /proc/stat 获取 CPU 使用情况

    Args:
        client: SSH 客户端

    Returns:
        CPU 使用信息
    """
    cpu_stats = {
        'user': 0,
        'nice': 0,
        'system': 0,
        'idle': 0,
        'iowait': 0,
        'irq': 0,
        'softirq': 0,
        'steal': 0,
        'guest': 0,
        'guest_nice': 0,
    }

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/stat 2>/dev/null")
        if exit_code != 0 or not stdout:
            return cpu_stats

        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith('cpu '):
                parts = line.split()
                if len(parts) >= 11:
                    cpu_stats['user'] = int(parts[1])
                    cpu_stats['nice'] = int(parts[2])
                    cpu_stats['system'] = int(parts[3])
                    cpu_stats['idle'] = int(parts[4])
                    cpu_stats['iowait'] = int(parts[5])
                    cpu_stats['irq'] = int(parts[6])
                    cpu_stats['softirq'] = int(parts[7])
                    cpu_stats['steal'] = int(parts[8])
                    cpu_stats['guest'] = int(parts[9])
                    cpu_stats['guest_nice'] = int(parts[10])
                break

    except Exception as e:
        logger.error(f"Error getting CPU usage from proc: {e}")

    return cpu_stats


def _get_load_average(client: SSHClient) -> Dict[str, float]:
    """
    获取系统负载平均值

    Args:
        client: SSH 客户端

    Returns:
        { 'load_1min': float, 'load_5min': float, 'load_15min': float }
    """
    load_avg = {
        'load_1min': 0.0,
        'load_5min': 0.0,
        'load_15min': 0.0,
    }

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/loadavg 2>/dev/null || uptime 2>/dev/null")
        if exit_code != 0 or not stdout:
            return load_avg

        if '/proc/loadavg' in stdout or len(stdout.split()) >= 3:
            parts = stdout.strip().split()
            try:
                if len(parts) >= 3:
                    load_avg['load_1min'] = float(parts[0])
                    load_avg['load_5min'] = float(parts[1])
                    load_avg['load_15min'] = float(parts[2])
            except (ValueError, IndexError):
                pass

    except Exception as e:
        logger.error(f"Error getting load average: {e}")

    return load_avg


def _get_per_core_usage(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取每核 CPU 使用情况

    Args:
        client: SSH 客户端

    Returns:
        每核 CPU 使用信息列表
    """
    per_core = []

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/stat 2>/dev/null")
        if exit_code != 0 or not stdout:
            return per_core

        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith('cpu') and not line.startswith('cpu '):
                parts = line.split()
                if len(parts) >= 5:
                    core_id = parts[0].replace('cpu', '')
                    per_core.append({
                        'core_id': core_id,
                        'user': int(parts[1]) if parts[1].isdigit() else 0,
                        'system': int(parts[3]) if parts[3].isdigit() else 0,
                        'idle': int(parts[4]) if parts[4].isdigit() else 0,
                    })

    except Exception as e:
        logger.error(f"Error getting per-core usage: {e}")

    return per_core


def collect_cpu_metrics(host: Host) -> Dict[str, Any]:
    """
    采集 CPU 监控数据

    Args:
        host: Host 模型实例

    Returns:
        CPU 监控数据
    """
    result = {
        'cpu_usage': {},
        'load_avg': {},
        'per_core': [],
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取 CPU 使用情况
            cpu_usage = _get_cpu_usage_from_proc(client)
            result['cpu_usage'] = cpu_usage

            # 计算使用率百分比
            total = sum(cpu_usage.values())
            if total > 0:
                idle = cpu_usage.get('idle', 0)
                result['cpu_usage']['usage_percent'] = round(100.0 * (total - idle) / total, 2)
            else:
                result['cpu_usage']['usage_percent'] = 0.0

            # 获取负载平均值
            load_avg = _get_load_average(client)
            result['load_avg'] = load_avg

            # 获取每核使用情况
            per_core = _get_per_core_usage(client)
            result['per_core'] = per_core

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect CPU metrics from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_memory_usage_from_proc(client: SSHClient) -> Dict[str, Any]:
    """
    从 /proc/meminfo 获取内存使用情况

    Args:
        client: SSH 客户端

    Returns:
        内存使用信息
    """
    meminfo = {
        'mem_total': 0,
        'mem_free': 0,
        'mem_available': 0,
        'mem_buffers': 0,
        'mem_cached': 0,
        'swap_total': 0,
        'swap_free': 0,
        'swap_cached': 0,
    }

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/meminfo 2>/dev/null")
        if exit_code != 0 or not stdout:
            return meminfo

        lines = stdout.strip().split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) >= 2:
                key = parts[0].strip()
                value_part = parts[1].strip().split()[0]
                value = int(value_part) if value_part.isdigit() else 0

                if key == 'MemTotal':
                    meminfo['mem_total'] = value
                elif key == 'MemFree':
                    meminfo['mem_free'] = value
                elif key == 'MemAvailable':
                    meminfo['mem_available'] = value
                elif key == 'Buffers':
                    meminfo['mem_buffers'] = value
                elif key == 'Cached':
                    meminfo['mem_cached'] = value
                elif key == 'SwapTotal':
                    meminfo['swap_total'] = value
                elif key == 'SwapFree':
                    meminfo['swap_free'] = value
                elif key == 'SwapCached':
                    meminfo['swap_cached'] = value

    except Exception as e:
        logger.error(f"Error getting memory usage from proc: {e}")

    return meminfo


def _get_swap_usage(client: SSHClient) -> Dict[str, Any]:
    """
    获取 Swap 使用情况

    Args:
        client: SSH 客户端

    Returns:
        Swap 使用信息
    """
    swap_info = {
        'swap_total': 0,
        'swap_used': 0,
        'swap_free': 0,
        'swap_percent': 0.0,
    }

    try:
        stdout, stderr, exit_code = client.execute_command("free -k 2>/dev/null")
        if exit_code != 0 or not stdout:
            return swap_info

        lines = stdout.strip().split('\n')
        for line in lines:
            if line.startswith('Swap:'):
                parts = line.split()
                if len(parts) >= 4:
                    swap_info['swap_total'] = int(parts[1])
                    swap_info['swap_used'] = int(parts[2])
                    swap_info['swap_free'] = int(parts[3])
                    if swap_info['swap_total'] > 0:
                        swap_info['swap_percent'] = round(100.0 * swap_info['swap_used'] / swap_info['swap_total'], 2)
                break

    except Exception as e:
        logger.error(f"Error getting swap usage: {e}")

    return swap_info


def collect_memory_metrics(host: Host) -> Dict[str, Any]:
    """
    采集内存监控数据

    Args:
        host: Host 模型实例

    Returns:
        内存监控数据
    """
    result = {
        'memory': {},
        'swap': {},
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取内存使用情况
            meminfo = _get_memory_usage_from_proc(client)
            result['memory'] = meminfo

            # 计算内存使用率
            if meminfo['mem_total'] > 0:
                mem_used = meminfo['mem_total'] - meminfo['mem_available']
                result['memory']['mem_used'] = mem_used
                result['memory']['mem_percent'] = round(100.0 * mem_used / meminfo['mem_total'], 2)

            # 获取 Swap 使用情况
            swap_info = _get_swap_usage(client)
            result['swap'] = swap_info

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect memory metrics from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_network_stats_from_proc(client: SSHClient) -> List[Dict[str, Any]]:
    """
    从 /proc/net/dev 获取网络接口统计

    Args:
        client: SSH 客户端

    Returns:
        网络接口统计列表
    """
    interfaces = []

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/net/dev 2>/dev/null")
        if exit_code != 0 or not stdout:
            return interfaces

        lines = stdout.strip().split('\n')
        # 跳过标题行
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                iface_part, stats_part = line.split(':', 1)
                iface_name = iface_part.strip()
                parts = stats_part.strip().split()

                if len(parts) >= 16:
                    interfaces.append({
                        'interface': iface_name,
                        'rx_bytes': int(parts[0]) if parts[0].isdigit() else 0,
                        'rx_packets': int(parts[1]) if parts[1].isdigit() else 0,
                        'rx_errors': int(parts[2]) if parts[2].isdigit() else 0,
                        'rx_drop': int(parts[3]) if parts[3].isdigit() else 0,
                        'tx_bytes': int(parts[8]) if parts[8].isdigit() else 0,
                        'tx_packets': int(parts[9]) if parts[9].isdigit() else 0,
                        'tx_errors': int(parts[10]) if parts[10].isdigit() else 0,
                        'tx_drop': int(parts[11]) if parts[11].isdigit() else 0,
                    })

    except Exception as e:
        logger.error(f"Error getting network stats from proc: {e}")

    return interfaces


def collect_network_metrics(host: Host) -> Dict[str, Any]:
    """
    采集网络监控数据

    Args:
        host: Host 模型实例

    Returns:
        网络监控数据
    """
    result = {
        'interfaces': [],
        'total_rx_bytes': 0,
        'total_tx_bytes': 0,
        'total_errors': 0,
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取网络接口统计
            interfaces = _get_network_stats_from_proc(client)
            result['interfaces'] = interfaces

            # 计算总计
            for iface in interfaces:
                result['total_rx_bytes'] += iface.get('rx_bytes', 0)
                result['total_tx_bytes'] += iface.get('tx_bytes', 0)
                result['total_errors'] += iface.get('rx_errors', 0) + iface.get('tx_errors', 0)

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect network metrics from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_disk_stats_from_proc(client: SSHClient) -> List[Dict[str, Any]]:
    """
    从 /proc/diskstats 获取磁盘统计

    Args:
        client: SSH 客户端

    Returns:
        磁盘统计列表
    """
    disks = []

    try:
        stdout, stderr, exit_code = client.execute_command("cat /proc/diskstats 2>/dev/null")
        if exit_code != 0 or not stdout:
            return disks

        lines = stdout.strip().split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 14:
                major = int(parts[0]) if parts[0].isdigit() else 0
                minor = int(parts[1]) if parts[1].isdigit() else 0
                dev_name = parts[2]

                # 只处理磁盘设备，跳过分区
                if dev_name.startswith(('sd', 'hd', 'vd', 'nvme')) and not any(c.isdigit() for c in dev_name):
                    disks.append({
                        'device': dev_name,
                        'major': major,
                        'minor': minor,
                        'reads_completed': int(parts[3]) if parts[3].isdigit() else 0,
                        'reads_merged': int(parts[4]) if parts[4].isdigit() else 0,
                        'sectors_read': int(parts[5]) if parts[5].isdigit() else 0,
                        'time_reading': int(parts[6]) if parts[6].isdigit() else 0,
                        'writes_completed': int(parts[7]) if parts[7].isdigit() else 0,
                        'writes_merged': int(parts[8]) if parts[8].isdigit() else 0,
                        'sectors_written': int(parts[9]) if parts[9].isdigit() else 0,
                        'time_writing': int(parts[10]) if parts[10].isdigit() else 0,
                        'io_in_progress': int(parts[11]) if parts[11].isdigit() else 0,
                        'time_io': int(parts[12]) if parts[12].isdigit() else 0,
                        'time_io_weighted': int(parts[13]) if parts[13].isdigit() else 0,
                    })

    except Exception as e:
        logger.error(f"Error getting disk stats from proc: {e}")

    return disks


def _get_partition_usage(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取分区使用情况

    Args:
        client: SSH 客户端

    Returns:
        分区使用情况列表
    """
    partitions = []

    try:
        stdout, stderr, exit_code = client.execute_command("df -kP 2>/dev/null")
        if exit_code != 0 or not stdout:
            return partitions

        lines = stdout.strip().split('\n')
        for line in lines[1:]:
            parts = line.strip().split()
            if len(parts) >= 6:
                try:
                    total = int(parts[1])
                    used = int(parts[2])
                    available = int(parts[3])
                    use_percent = float(parts[4].replace('%', '')) if '%' in parts[4] else 0.0

                    partitions.append({
                        'filesystem': parts[0],
                        'total_kb': total,
                        'used_kb': used,
                        'available_kb': available,
                        'use_percent': use_percent,
                        'mount_point': parts[5],
                    })
                except (ValueError, IndexError):
                    continue

    except Exception as e:
        logger.error(f"Error getting partition usage: {e}")

    return partitions


def collect_disk_metrics(host: Host) -> Dict[str, Any]:
    """
    采集磁盘监控数据

    Args:
        host: Host 模型实例

    Returns:
        磁盘监控数据
    """
    result = {
        'disks': [],
        'partitions': [],
        'collected_at': '',
        'success': False,
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取磁盘统计
            disks = _get_disk_stats_from_proc(client)
            result['disks'] = disks

            # 获取分区使用情况
            partitions = _get_partition_usage(client)
            result['partitions'] = partitions

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect disk metrics from host {host.id}: {e}")
        result['error'] = str(e)

    return result