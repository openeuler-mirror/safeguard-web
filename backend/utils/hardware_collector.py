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
        import shlex
        # Validate service_name: only allow alphanumeric, -, _, .
        if not service_name or not all(c.isalnum() or c in '-_.' for c in service_name):
            return 'unknown'
        safe_service_name = shlex.quote(service_name)
        stdout, stderr, exit_code = client.execute_command(
            f"systemctl is-enabled {safe_service_name} 2>/dev/null"
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
        import shlex
        # Validate action: only allow specific values
        allowed_actions = ['start', 'stop', 'restart', 'reload', 'enable', 'disable']
        if action not in allowed_actions:
            return False
        # Validate service_name
        if not service_name or not all(c.isalnum() or c in '-_.' for c in service_name):
            return False
        safe_service_name = shlex.quote(service_name)
        stdout, stderr, exit_code = client.execute_command(
            f"systemctl {action} {safe_service_name} 2>&1"
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
                is_disk = False
                if dev_name.startswith(('sd', 'hd', 'vd')):
                    # 传统磁盘: sda, sdb, hda, vda - 分区有数字后缀
                    is_disk = not any(c.isdigit() for c in dev_name)
                elif dev_name.startswith('nvme'):
                    # NVMe磁盘: nvme0n1, nvme1n1 - 分区是 nvme0n1p1, nvme0n1p2
                    # 匹配 nvmeXnY 格式，不匹配 nvmeXnYpZ
                    is_disk = bool(re.match(r'nvme\d+n\d+$', dev_name))

                if is_disk:
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


def _get_system_accounts(client: SSHClient) -> List[Dict[str, Any]]:
    """
    获取系统账户列表

    Args:
        client: SSH 客户端

    Returns:
        系统账户列表
    """
    accounts = []
    try:
        # 使用 cat /etc/passwd 获取账户信息
        stdout, stderr, exit_code = client.execute_command("cat /etc/passwd 2>/dev/null")
        if exit_code != 0 or not stdout:
            return accounts

        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split(':')
            if len(parts) < 7:
                continue

            username = parts[0]
            password = parts[1]
            uid = int(parts[2]) if parts[2].isdigit() else -1
            gid = int(parts[3]) if parts[3].isdigit() else -1
            gecos = parts[4]
            home_dir = parts[5]
            shell = parts[6]

            # 判断账户类型
            is_system = uid < 1000

            accounts.append({
                'username': username,
                'uid': uid,
                'gid': gid,
                'gecos': gecos,
                'home_dir': home_dir,
                'shell': shell,
                'is_system': is_system,
                'is_locked': password.startswith('!') or password.startswith('*'),
            })

    except Exception as e:
        logger.error(f"Error getting system accounts: {e}")

    return accounts


def _get_account_password_info(client: SSHClient, username: str) -> Dict[str, Any]:
    """
    获取账户密码信息

    Args:
        client: SSH 客户端
        username: 用户名

    Returns:
        密码信息字典
    """
    info = {
        'password_changed': None,
        'password_expires': None,
        'min_days': -1,
        'max_days': -1,
        'warn_days': -1,
    }

    try:
        import shlex
        # Validate username: only allow alphanumeric, -, _, .
        if not username or not all(c.isalnum() or c in '-_.' for c in username):
            return info
        safe_username = shlex.quote(username)
        stdout, stderr, exit_code = client.execute_command(f"chage -l {safe_username} 2>/dev/null")
        if exit_code != 0 or not stdout:
            return info

        lines = stdout.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if 'last password change' in key:
                    if value and value != 'never':
                        try:
                            info['password_changed'] = value
                        except:
                            pass
                elif 'password expires' in key:
                    if value and value != 'never':
                        try:
                            info['password_expires'] = value
                        except:
                            pass
                elif 'minimum' in key and 'days' in key:
                    try:
                        info['min_days'] = int(value) if value.isdigit() else -1
                    except:
                        pass
                elif 'maximum' in key and 'days' in key:
                    try:
                        info['max_days'] = int(value) if value.isdigit() else -1
                    except:
                        pass
                elif 'warning' in key and 'days' in key:
                    try:
                        info['warn_days'] = int(value) if value.isdigit() else -1
                    except:
                        pass

    except Exception as e:
        logger.error(f"Error getting account password info for {username}: {e}")

    return info


def _get_last_login_info(client: SSHClient, username: str) -> Dict[str, Any]:
    """
    获取账户最后登录信息

    Args:
        client: SSH 客户端
        username: 用户名

    Returns:
        最后登录信息字典
    """
    info = {
        'last_login': None,
        'login_count': 0,
    }

    try:
        import shlex
        # Validate username
        if not username or not all(c.isalnum() or c in '-_.' for c in username):
            return info
        safe_username = shlex.quote(username)
        # 使用 last 命令获取最后登录信息
        stdout, stderr, exit_code = client.execute_command(f"last -n 10 {safe_username} 2>/dev/null")
        if exit_code == 0 and stdout:
            lines = stdout.strip().split('\n')
            login_count = 0
            for line in lines:
                line = line.strip()
                if line.startswith(username):
                    login_count += 1
                    if not info['last_login']:
                        # 提取最后登录时间
                        parts = line.split()
                        if len(parts) >= 7:
                            info['last_login'] = ' '.join(parts[3:7])
            info['login_count'] = login_count

    except Exception as e:
        logger.error(f"Error getting last login info for {username}: {e}")

    return info


def collect_system_accounts(host: Host) -> Dict[str, Any]:
    """
    采集系统账户信息

    Args:
        host: Host 模型实例

    Returns:
        系统账户信息字典
    """
    result = {
        'success': False,
        'accounts': [],
        'total_accounts': 0,
        'system_accounts': 0,
        'user_accounts': 0,
        'collected_at': '',
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 获取系统账户列表
            accounts = _get_system_accounts(client)

            # 为每个账户获取详细信息
            for account in accounts:
                username = account['username']
                # 获取密码信息
                password_info = _get_account_password_info(client, username)
                account.update(password_info)

                # 获取最后登录信息
                login_info = _get_last_login_info(client, username)
                account.update(login_info)

            result['accounts'] = accounts
            result['total_accounts'] = len(accounts)
            result['system_accounts'] = len([a for a in accounts if a['is_system']])
            result['user_accounts'] = len([a for a in accounts if not a['is_system']])
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect system accounts from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _parse_syslog_line(line: str) -> Optional[Dict[str, Any]]:
    """
    解析系统日志行

    Args:
        line: 日志行文本

    Returns:
        解析后的日志字典，或 None
    """
    try:
        line = line.strip()
        if not line:
            return None

        # 尝试解析标准的 syslog 格式
        # 格式: <month> <day> <time> <hostname> <process>: <message>
        parts = line.split(None, 5)
        if len(parts) >= 6:
            month = parts[0]
            day = parts[1]
            time_str = parts[2]
            hostname = parts[3]
            process = parts[4].rstrip(':')
            message = parts[5]

            # 提取进程ID (如果有)
            pid = None
            process_name = process
            if '[' in process and ']' in process:
                pid_match = process.split('[')[1].rstrip(']')
                if pid_match.isdigit():
                    pid = int(pid_match)
                process_name = process.split('[')[0]

            # 判断日志级别
            level = 'info'
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in ['error', 'err', 'critical', 'fatal']):
                level = 'error'
            elif any(keyword in message_lower for keyword in ['warning', 'warn']):
                level = 'warning'
            elif any(keyword in message_lower for keyword in ['debug']):
                level = 'debug'

            return {
                'timestamp': f"{month} {day} {time_str}",
                'hostname': hostname,
                'process': process_name,
                'pid': pid,
                'message': message,
                'level': level,
                'raw_line': line,
            }

    except Exception as e:
        logger.debug(f"Failed to parse syslog line: {e}")

    return None


def _collect_logs_from_file(client: SSHClient, log_path: str, num_lines: int = 100) -> List[Dict[str, Any]]:
    """
    从指定文件中收集日志

    Args:
        client: SSH 客户端
        log_path: 日志文件路径
        num_lines: 收集的行数

    Returns:
        日志列表
    """
    logs = []
    try:
        # Validate num_lines: must be integer between 1 and 10000
        if not isinstance(num_lines, int):
            try:
                num_lines = int(num_lines)
            except (ValueError, TypeError):
                num_lines = 100
        num_lines = max(1, min(num_lines, 10000))

        # Validate log_path: should start with / and not contain shell metacharacters
        if not log_path.startswith('/'):
            return logs
        # Disallow shell metacharacters in log_path
        if any(c in log_path for c in [';', '|', '&', '>', '<', '`', '$', '(', ')', '[', ']', '{', '}', '*', '?', '~', "'", '"', '\\']):
            return logs

        # Use single quotes around log_path to prevent shell expansion
        # Use printf to safely format the command
        import shlex
        safe_log_path = shlex.quote(log_path)
        stdout, stderr, exit_code = client.execute_command(f"tail -n {num_lines} {safe_log_path} 2>/dev/null")
        if exit_code != 0 or not stdout:
            return logs

        lines = stdout.strip().split('\n')
        for line in lines:
            parsed_log = _parse_syslog_line(line)
            if parsed_log:
                logs.append(parsed_log)

    except Exception as e:
        logger.error(f"Error collecting logs from {log_path}: {e}")

    return logs


def collect_system_logs(host: Host, log_sources: Optional[List[str]] = None, num_lines: int = 100) -> Dict[str, Any]:
    """
    采集系统日志

    Args:
        host: Host 模型实例
        log_sources: 日志源列表（默认包含常见系统日志）
        num_lines: 每个源采集的行数

    Returns:
        系统日志信息字典
    """
    if log_sources is None:
        log_sources = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/auth.log',
            '/var/log/secure',
            '/var/log/kern.log',
            '/var/log/dmesg',
        ]

    result = {
        'success': False,
        'logs': [],
        'sources_collected': [],
        'total_logs': 0,
        'collected_at': '',
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            all_logs = []

            for log_path in log_sources:
                # Validate log path first
                if not log_path.startswith('/'):
                    continue
                if any(c in log_path for c in [';', '|', '&', '>', '<', '`', '$', '(', ')', '[', ']', '{', '}', '*', '?', '~', "'", '"', '\\']):
                    continue
                # 检查文件是否存在 using file_exists method instead of shell command
                if not client.file_exists(log_path):
                    continue

                # 收集日志
                logs = _collect_logs_from_file(client, log_path, num_lines)
                if logs:
                    # 添加源信息
                    for log in logs:
                        log['source'] = log_path
                    all_logs.extend(logs)
                    result['sources_collected'].append(log_path)

            # 按时间倒序排序
            all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            result['logs'] = all_logs
            result['total_logs'] = len(all_logs)
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect system logs from host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _get_available_log_sources(client: SSHClient) -> List[str]:
    """
    获取可用的日志源列表

    Args:
        client: SSH 客户端

    Returns:
        可用日志源列表
    """
    sources = []
    try:
        # 常见的日志目录和文件
        common_paths = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/auth.log',
            '/var/log/secure',
            '/var/log/kern.log',
            '/var/log/dmesg',
            '/var/log/daemon.log',
            '/var/log/user.log',
            '/var/log/cron.log',
        ]

        for path in common_paths:
            check_cmd = f"test -f {path} && echo exists || echo not_exists"
            stdout, stderr, exit_code = client.execute_command(check_cmd)
            if stdout.strip() == 'exists':
                sources.append(path)

    except Exception as e:
        logger.error(f"Error getting available log sources: {e}")

    return sources


def control_service(host: Host, service_name: str, action: str) -> Dict[str, Any]:
    """
    控制主机服务（启动、停止、重启、重载、启用、禁用）

    Args:
        host: Host 模型实例
        service_name: 服务名称
        action: 操作类型 - 'start' | 'stop' | 'restart' | 'reload' | 'enable' | 'disable'

    Returns:
        操作结果字典
    """
    result = {
        'success': False,
        'message': '',
        'service_name': service_name,
        'action': action,
        'collected_at': '',
        'stdout': '',
        'stderr': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 构建命令
            if action in ['enable', 'disable']:
                cmd = f"systemctl {action} {service_name} 2>&1"
            else:
                cmd = f"systemctl {action} {service_name} 2>&1"

            stdout, stderr, exit_code = client.execute_command(cmd)

            result['stdout'] = stdout
            result['stderr'] = stderr

            if exit_code == 0:
                result['success'] = True
                result['message'] = f"Service {service_name} {action} successful"
            else:
                result['success'] = False
                result['message'] = f"Service {service_name} {action} failed: {stderr or stdout}"

            # 记录操作时间
            result['collected_at'] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Failed to {action} service {service_name} on host {host.id}: {e}")
        result['message'] = str(e)
        result['error'] = str(e)

    return result


def get_service_logs(host: Host, service_name: str, lines: int = 100) -> Dict[str, Any]:
    """
    获取服务日志

    Args:
        host: Host 模型实例
        service_name: 服务名称
        lines: 获取日志行数

    Returns:
        日志信息字典
    """
    result = {
        'success': False,
        'logs': [],
        'service_name': service_name,
        'collected_at': '',
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            # 使用 journalctl 获取服务日志
            cmd = f"journalctl -u {service_name} -n {lines} --no-pager 2>&1"
            stdout, stderr, exit_code = client.execute_command(cmd)

            if exit_code == 0 and stdout:
                log_lines = stdout.strip().split('\n')
                parsed_logs = []
                for line in log_lines:
                    parsed = _parse_syslog_line(line)
                    if parsed:
                        parsed_logs.append(parsed)
                    else:
                        parsed_logs.append({'raw_line': line})
                result['logs'] = parsed_logs
                result['success'] = True
            else:
                # 尝试从常见日志文件查找
                log_paths = [
                    f'/var/log/{service_name}.log',
                    f'/var/log/{service_name}/{service_name}.log',
                    '/var/log/syslog',
                    '/var/log/messages',
                ]
                for log_path in log_paths:
                    logs = _collect_logs_from_file(client, log_path, lines)
                    if logs:
                        result['logs'] = logs
                        result['success'] = True
                        break

            # 记录采集时间
            result['collected_at'] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Failed to get service logs for {service_name} on host {host.id}: {e}")
        result['error'] = str(e)

    return result


def _kill_process(client: SSHClient, pid: int, force: bool = False) -> Dict[str, Any]:
    """
    终止进程

    Args:
        client: SSH 客户端
        pid: 进程ID
        force: 是否强制终止（使用 SIGKILL）

    Returns:
        操作结果字典
    """
    result = {
        'success': False,
        'message': '',
        'pid': pid,
    }

    try:
        # 检查进程是否存在
        check_cmd = f"ps -p {pid} -o pid= 2>/dev/null"
        stdout, stderr, exit_code = client.execute_command(check_cmd)
        if exit_code != 0 or not stdout.strip():
            result['message'] = f"Process {pid} not found"
            return result

        # 终止进程
        signal = '-9' if force else '-15'
        kill_cmd = f"kill {signal} {pid} 2>&1"
        stdout, stderr, exit_code = client.execute_command(kill_cmd)

        if exit_code == 0:
            result['success'] = True
            result['message'] = f"Process {pid} killed successfully"
        else:
            result['message'] = f"Failed to kill process {pid}: {stderr or stdout}"

    except Exception as e:
        logger.error(f"Error killing process {pid}: {e}")
        result['message'] = str(e)

    return result


def kill_process(host: Host, pid: int, force: bool = False) -> Dict[str, Any]:
    """
    终止主机上的进程

    Args:
        host: Host 模型实例
        pid: 进程ID
        force: 是否强制终止

    Returns:
        操作结果字典
    """
    result = {
        'success': False,
        'message': '',
        'pid': pid,
        'collected_at': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            kill_result = _kill_process(client, pid, force)
            result.update(kill_result)
            result['collected_at'] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Failed to kill process {pid} on host {host.id}: {e}")
        result['message'] = str(e)
        result['error'] = str(e)

    return result


def _collect_file_events(client: SSHClient, monitor_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    收集文件监控事件（通过检查文件状态变化）

    Args:
        client: SSH 客户端
        monitor_rules: 监控规则列表

    Returns:
        文件事件列表
    """
    events = []

    try:
        for rule in monitor_rules:
            path = rule.get('path', '')
            if not path:
                continue

            # 检查路径是否存在
            check_cmd = f"test -e {path} && echo exists || echo not_exists"
            stdout, stderr, exit_code = client.execute_command(check_cmd)
            exists = stdout.strip() == 'exists'

            if not exists:
                events.append({
                    'rule_id': rule.get('id'),
                    'path': path,
                    'event_type': 'path_not_exists',
                    'timestamp': datetime.now().isoformat(),
                    'details': 'Path does not exist',
                })
                continue

            # 获取文件状态信息
            stat_cmd = f"stat -c '%Y:%Z:%s:%u:%g:%a' {path} 2>/dev/null"
            stdout, stderr, exit_code = client.execute_command(stat_cmd)
            if exit_code == 0 and stdout:
                parts = stdout.strip().split(':')
                if len(parts) >= 6:
                    mtime = int(parts[0])
                    ctime = int(parts[1])
                    size = int(parts[2])
                    uid = int(parts[3])
                    gid = int(parts[4])
                    mode = parts[5]

                    # 转换时间戳
                    mtime_dt = datetime.fromtimestamp(mtime).isoformat()
                    ctime_dt = datetime.fromtimestamp(ctime).isoformat()

                    events.append({
                        'rule_id': rule.get('id'),
                        'path': path,
                        'event_type': 'file_status',
                        'timestamp': datetime.now().isoformat(),
                        'details': {
                            'mtime': mtime_dt,
                            'ctime': ctime_dt,
                            'size': size,
                            'uid': uid,
                            'gid': gid,
                            'mode': mode,
                        },
                    })

            # 如果是目录且启用递归监控
            if rule.get('recursive', False):
                ls_cmd = f"ls -la --time-style=full-iso {path} 2>/dev/null"
                stdout, stderr, exit_code = client.execute_command(ls_cmd)
                if exit_code == 0 and stdout:
                    events.append({
                        'rule_id': rule.get('id'),
                        'path': path,
                        'event_type': 'directory_listing',
                        'timestamp': datetime.now().isoformat(),
                        'details': {'listing': stdout},
                    })

    except Exception as e:
        logger.error(f"Error collecting file events: {e}")

    return events


def collect_file_events(host: Host, monitor_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    收集文件监控事件

    Args:
        host: Host 模型实例
        monitor_rules: 监控规则列表

    Returns:
        文件监控事件字典
    """
    result = {
        'success': False,
        'events': [],
        'total_events': 0,
        'collected_at': '',
        'error': '',
    }

    try:
        with SSHClient(
            host=host.ip_address,
            port=host.port,
            username=host.username,
            password=host.password,
        ) as client:
            events = _collect_file_events(client, monitor_rules)
            result['events'] = events
            result['total_events'] = len(events)
            result['collected_at'] = datetime.now().isoformat()
            result['success'] = True

    except Exception as e:
        logger.error(f"Failed to collect file events on host {host.id}: {e}")
        result['error'] = str(e)

    return result