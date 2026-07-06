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