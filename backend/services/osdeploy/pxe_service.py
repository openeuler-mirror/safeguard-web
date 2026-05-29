"""PXE 配置生成服务"""
import os
import logging
from typing import List, Optional
from backend.models.osdeploy import PXEServerStatus, KickStartFileStatus

logger = logging.getLogger(__name__)


class DHCPSubnet:
    """DHCP 子网配置"""
    def __init__(self, network: str, next_server: str, netmask: str, router: str,
                 bootp_start: str = None, bootp_end: str = None):
        self.network = network
        self.next_server = next_server
        self.netmask = netmask
        self.router = router
        self.bootp_start = bootp_start
        self.bootp_end = bootp_end


class PXEService:
    """PXE 配置服务"""

    @staticmethod
    def generate_dhcp_config(subnets: List[DHCPSubnet]) -> str:
        """生成DHCP配置文件内容"""
        config = """# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd.conf.example
#   see dhcpd.conf(5) man page

option architecture-type code 93 = unsigned integer 16;
"""
        classes = [
            {
                "name": "HW-client",
                "vendor_id": "HW-Client",
                "arch_type": "00:0b",
                "filename": "grubaa64.efi",
                "alt_filename": None,
            },
            {
                "name": "pxeclients",
                "vendor_id": "PXEClient",
                "arch_type": "00:07",
                "filename": "grubx64.efi",
                "alt_filename": "pxelinux.0",
            },
        ]

        for subnet in subnets:
            config += f"subnet {subnet.network} netmask {subnet.netmask} {{\n"
            config += f"\toption routers {subnet.router};\n"
            if subnet.bootp_start and subnet.bootp_end:
                config += f"\trange {subnet.bootp_start} {subnet.bootp_end};\n"
            config += f"\tnext-server {subnet.next_server};\n\n"

            for cls in classes:
                config += f'\tclass "{cls["name"]}" {{\n'
                config += f'\t\tmatch if substring (option vendor-class-identifier, 0, 9) = "{cls["vendor_id"]}";\n'
                config += f'\t\tif option architecture-type = {cls["arch_type"]} {{\n'
                config += f'\t\t\tfilename "{cls["filename"]}";\n'
                if cls["alt_filename"]:
                    config += '\t\t} else {\n'
                    config += f'\t\t\tfilename "{cls["alt_filename"]}";\n'
                config += '\t\t}\n'
                config += '\t}\n\n'

            config += "}\n\n"

        return config

    @staticmethod
    def write_dhcp_config(content: str, config_path: str = "/etc/dhcp/dhcpd.conf") -> bool:
        """写入DHCP配置文件"""
        try:
            with open(config_path, 'w') as f:
                f.write(content)
            logger.info(f"DHCP配置已写入: {config_path}")
            return True
        except PermissionError:
            logger.error(f"权限不足，无法写入DHCP配置: {config_path}")
            return False
        except Exception as e:
            logger.error(f"写入DHCP配置失败: {e}")
            return False

    @staticmethod
    def generate_pxe_boot_file(mac_address: str, ks_url: str, repo_url: str,
                                os_type: str = "culinux") -> str:
        """生成PXE启动配置文件内容"""
        mac_hex = mac_address.replace(":", "").lower()
        if os_type in ["centos7", "openeuler"]:
            content = f"""default auto
prompt 0
timeout 30

label auto
  kernel {os_type}/vmlinuz
  append initrd={os_type}/initrd.img ks={ks_url} repo={repo_url} ip=dhcp quiet
"""
        else:
            content = f"""default auto
prompt 0
timeout 30

label auto
  kernel vmlinuz
  append initrd=initrd.img ks={ks_url} ip=dhcp quiet
"""
        return content

    @staticmethod
    def write_pxe_boot_file(mac_address: str, content: str,
                            tftp_dir: str = "/var/lib/tftpboot/pxelinux.cfg") -> bool:
        """写入PXE启动配置文件"""
        try:
            mac_hex = mac_address.replace(":", "").lower()
            # PXE 配置文件名格式: 01-<MAC地址> (带冒号)
            filename = f"01-{mac_address.lower()}"
            filepath = os.path.join(tftp_dir, filename)

            os.makedirs(tftp_dir, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"PXE启动配置已写入: {filepath}")
            return True
        except PermissionError:
            logger.error(f"权限不足，无法写入PXE启动配置")
            return False
        except Exception as e:
            logger.error(f"写入PXE启动配置失败: {e}")
            return False

    @staticmethod
    def remove_pxe_boot_file(mac_address: str,
                             tftp_dir: str = "/var/lib/tftpboot/pxelinux.cfg") -> bool:
        """删除PXE启动配置文件（装机完成后清理）"""
        try:
            filename = f"01-{mac_address.lower()}"
            filepath = os.path.join(tftp_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"PXE启动配置已删除: {filepath}")
            return True
        except Exception as e:
            logger.error(f"删除PXE启动配置失败: {e}")
            return False

    @staticmethod
    def get_ks_url(server_ip: str, ks_name: str) -> str:
        """生成Kickstart URL"""
        return f"http://{server_ip}/pxe/{ks_name}"

    @staticmethod
    def get_repo_url(server_ip: str, repo_name: str) -> str:
        """生成仓库URL"""
        return f"http://{server_ip}/repo/{repo_name}"