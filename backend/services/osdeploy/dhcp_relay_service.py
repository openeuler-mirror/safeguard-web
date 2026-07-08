"""DHCP Relay 服务"""
import logging
from typing import Dict

from backend.utils.ssh import SSHClient
from backend.common import HostConnectionError, OperationError

logger = logging.getLogger(__name__)


class DHCPRelayService:
    """DHCP Relay 配置服务"""

    @staticmethod
    def configure_relay(params: Dict[str, str]) -> Dict[str, str]:
        """配置 DHCP Relay"""
        host = params.get("host")
        port = int(params.get("port", "22"))
        username = params.get("username")
        password = params.get("password")
        interface = params.get("interface_name")
        relay_ip = params.get("dhcp_relay_ip")

        if not all([host, username, password, interface, relay_ip]):
            raise OperationError("缺少必要参数")

        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            raise HostConnectionError(f"无法连接到主机 {host}")

        try:
            cmds = [
                "system-view",
                "dhcp enable",
                f"interface {interface}",
                "dhcp select relay",
                f"dhcp relay server-address {relay_ip}",
                "local-proxy-arp enable",
                "proxy-arp enable",
                "quit",
                "quit",
            ]
            command = "\n".join(cmds) + "\n"
            stdout, stderr, exit_code = ssh.execute_command(command)
            if exit_code != 0:
                raise OperationError(f"配置失败: {stderr}")
            return {"message": "DHCP Relay 配置成功", "output": stdout}
        finally:
            ssh.close()

    @staticmethod
    def display_relay(params: Dict[str, str]) -> Dict[str, str]:
        """展示 DHCP Relay 配置"""
        host = params.get("host")
        port = int(params.get("port", "22"))
        username = params.get("username")
        password = params.get("password")
        interface = params.get("interface_name")

        if not all([host, username, password, interface]):
            raise OperationError("缺少必要参数")

        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            raise HostConnectionError(f"无法连接到主机 {host}")

        try:
            cmds = [
                "system-view",
                f"interface {interface}",
                "display dhcp relay server-address",
                "display local-proxy-arp",
                "display proxy-arp",
            ]
            command = "\n".join(cmds) + "\n"
            stdout, stderr, exit_code = ssh.execute_command(command)
            if exit_code != 0:
                raise OperationError(f"查询失败: {stderr}")
            return {"message": "查询成功", "output": stdout}
        finally:
            ssh.close()

    @staticmethod
    def undo_relay(params: Dict[str, str]) -> Dict[str, str]:
        """撤销 DHCP Relay 配置"""
        host = params.get("host")
        port = int(params.get("port", "22"))
        username = params.get("username")
        password = params.get("password")
        interface = params.get("interface_name")
        relay_ip = params.get("dhcp_relay_ip")

        if not all([host, username, password, interface, relay_ip]):
            raise OperationError("缺少必要参数")

        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            raise HostConnectionError(f"无法连接到主机 {host}")

        try:
            cmds = [
                "system-view",
                "undo dhcp enable",
                f"interface {interface}",
                "undo dhcp select relay",
                f"undo dhcp relay server-address {relay_ip}",
                "undo local-proxy-arp enable",
                "undo proxy-arp enable",
                "quit",
                "quit",
            ]
            command = "\n".join(cmds) + "\n"
            stdout, stderr, exit_code = ssh.execute_command(command)
            if exit_code != 0:
                raise OperationError(f"撤销失败: {stderr}")
            return {"message": "DHCP Relay 撤销成功", "output": stdout}
        finally:
            ssh.close()
