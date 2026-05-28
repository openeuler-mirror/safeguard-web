"""
硬件信息采集工具

通过 SSH 连接到远程主机，采集硬件信息（CPU、内存、磁盘、网络等）
"""
import logging
from typing import Dict, List, Optional, Tuple
from backend.models.host import Host
from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)


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