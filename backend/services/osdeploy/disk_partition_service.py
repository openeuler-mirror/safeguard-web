"""磁盘分区服务"""
import logging
import json
from typing import Dict, List

from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)


class DiskPartitionService:
    """磁盘分区管理服务"""

    @staticmethod
    def get_disk_info(host: str, port: int, username: str, password: str) -> Dict:
        """获取远程主机磁盘信息"""
        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            return {"status": "failed", "message": f"无法连接到主机 {host}"}

        try:
            # 使用 lsblk 获取磁盘信息
            stdout, stderr, exit_code = ssh.execute_command("lsblk -J -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,MODEL")
            if exit_code != 0:
                return {"status": "failed", "message": f"获取磁盘信息失败: {stderr}"}

            try:
                disk_data = json.loads(stdout)
            except json.JSONDecodeError:
                return {"status": "failed", "message": "解析磁盘信息失败"}

            disks = []
            for device in disk_data.get("blockdevices", []):
                if device.get("type") == "disk":
                    disks.append({
                        "name": device.get("name"),
                        "size": device.get("size"),
                        "model": device.get("model", ""),
                        "children": device.get("children", []),
                    })

            return {"status": "success", "disks": disks}
        finally:
            ssh.close()

    @staticmethod
    def is_system_disk(disk_name: str, host: str, port: int, username: str, password: str) -> bool:
        """判断是否为系统盘"""
        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            return False

        try:
            # 检查挂载点是否包含 /
            stdout, _, _ = ssh.execute_command(f"lsblk -o MOUNTPOINT /dev/{disk_name} 2>/dev/null | grep -w '/'")
            return bool(stdout.strip())
        finally:
            ssh.close()

    @staticmethod
    def is_free_disk(disk_name: str, host: str, port: int, username: str, password: str) -> bool:
        """判断磁盘是否空闲（无分区或全部分区未挂载）"""
        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            return False

        try:
            stdout, _, _ = ssh.execute_command(f"lsblk -o MOUNTPOINT /dev/{disk_name} 2>/dev/null | grep -v '^$' | grep -v 'MOUNTPOINT'")
            return not stdout.strip()
        finally:
            ssh.close()

    @staticmethod
    def execute_partition(disk_name: str, mode: str, scheme: Dict,
                          host: str, port: int, username: str, password: str) -> Dict:
        """执行分区方案

        Args:
            disk_name: 磁盘名（如 sdb）
            mode: Global / Free
            scheme: 分区方案 {"partitions": [{"size": "100G", "fstype": "ext4", "mountpoint": "/data"}]}
            host, port, username, password: 远程主机连接信息
        """
        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            return {"status": "failed", "message": f"无法连接到主机 {host}"}

        try:
            # 验证模式
            if mode == "Global":
                if DiskPartitionService.is_system_disk(disk_name, host, port, username, password):
                    return {"status": "failed", "message": "Global 模式下不能操作系统盘"}
            elif mode == "Free":
                if not DiskPartitionService.is_free_disk(disk_name, host, port, username, password):
                    return {"status": "failed", "message": "该磁盘不是空闲磁盘，无法分区"}

            # 使用 parted 进行分区
            device = f"/dev/{disk_name}"
            partitions = scheme.get("partitions", [])

            # 创建 GPT 标签
            stdout, stderr, exit_code = ssh.execute_command(f"parted -s {device} mklabel gpt")
            if exit_code != 0:
                return {"status": "failed", "message": f"创建 GPT 标签失败: {stderr}"}

            for idx, part in enumerate(partitions, start=1):
                size = part.get("size", "100%")
                fstype = part.get("fstype", "ext4")
                mountpoint = part.get("mountpoint", f"/data{idx}")

                # 创建分区
                if size == "100%":
                    cmd = f"parted -s {device} mkpart primary {fstype} 0% 100%"
                else:
                    cmd = f"parted -s {device} mkpart primary {fstype} 0% {size}"
                stdout, stderr, exit_code = ssh.execute_command(cmd)
                if exit_code != 0:
                    return {"status": "failed", "message": f"创建分区失败: {stderr}"}

                # 格式化
                part_device = f"{device}{idx}"
                stdout, stderr, exit_code = ssh.execute_command(f"mkfs.{fstype} {part_device} 2>/dev/null || mkfs -t {fstype} {part_device}")
                if exit_code != 0:
                    return {"status": "failed", "message": f"格式化分区失败: {stderr}"}

                # 创建挂载点并挂载
                ssh.execute_command(f"mkdir -p {mountpoint}")
                stdout, stderr, exit_code = ssh.execute_command(f"mount {part_device} {mountpoint}")
                if exit_code != 0:
                    return {"status": "failed", "message": f"挂载分区失败: {stderr}"}

                # 写入 /etc/fstab
                ssh.execute_command(f"echo '{part_device} {mountpoint} {fstype} defaults 0 0' >> /etc/fstab")

            return {"status": "success", "message": f"磁盘 {disk_name} 分区完成"}
        finally:
            ssh.close()
