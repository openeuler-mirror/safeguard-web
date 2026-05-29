"""DHCP服务"""
import subprocess
import logging
from typing import Optional
from backend.models.osdeploy import PXEServerStatus, WhiteList

logger = logging.getLogger(__name__)


class DHCPService:
    """DHCP服务"""

    _is_running = False

    @staticmethod
    def start_dhcp_service() -> dict:
        """启动DHCP服务"""
        try:
            result = subprocess.run(
                ["systemctl", "start", "dhcpd"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                DHCPService._is_running = True
                return {"status": "success", "message": "DHCP服务启动成功"}
            else:
                logger.error(f"启动DHCP服务失败: {result.stderr}")
                return {"status": "failed", "message": result.stderr or "启动失败"}
        except FileNotFoundError:
            logger.warning("systemctl 未找到，尝试使用 service 命令")
            try:
                result = subprocess.run(
                    ["service", "dhcpd", "start"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    DHCPService._is_running = True
                    return {"status": "success", "message": "DHCP服务启动成功"}
                else:
                    return {"status": "failed", "message": result.stderr or "启动失败"}
            except Exception as e:
                logger.error(f"启动DHCP服务异常: {e}")
                return {"status": "failed", "message": str(e)}
        except Exception as e:
            logger.error(f"启动DHCP服务异常: {e}")
            return {"status": "failed", "message": str(e)}

    @staticmethod
    def stop_dhcp_service() -> dict:
        """停止DHCP服务"""
        try:
            result = subprocess.run(
                ["systemctl", "stop", "dhcpd"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                DHCPService._is_running = False
                return {"status": "success", "message": "DHCP服务停止成功"}
            else:
                logger.error(f"停止DHCP服务失败: {result.stderr}")
                return {"status": "failed", "message": result.stderr or "停止失败"}
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    ["service", "dhcpd", "stop"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    DHCPService._is_running = False
                    return {"status": "success", "message": "DHCP服务停止成功"}
                else:
                    return {"status": "failed", "message": result.stderr or "停止失败"}
            except Exception as e:
                logger.error(f"停止DHCP服务异常: {e}")
                return {"status": "failed", "message": str(e)}
        except Exception as e:
            logger.error(f"停止DHCP服务异常: {e}")
            return {"status": "failed", "message": str(e)}

    @staticmethod
    def restart_dhcp_service() -> dict:
        """重启DHCP服务"""
        stop_result = DHCPService.stop_dhcp_service()
        if stop_result["status"] == "failed":
            return stop_result
        return DHCPService.start_dhcp_service()

    @staticmethod
    def is_dhcp_running() -> bool:
        """检查DHCP服务状态"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "dhcpd"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            is_active = result.returncode == 0 and result.stdout.strip() == "active"
            DHCPService._is_running = is_active
            return is_active
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    ["service", "dhcpd", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                is_active = result.returncode == 0 and "running" in result.stdout.lower()
                DHCPService._is_running = is_active
                return is_active
            except Exception:
                return DHCPService._is_running
        except Exception:
            return DHCPService._is_running

    @staticmethod
    def setup_dhcp(server_ip: str, interface: str, range_start: str, range_end: str, subnet: str = None, gateway: str = None) -> PXEServerStatus:
        """配置DHCP服务"""
        # TODO: 实现实际的DHCP服务配置逻辑
        # 例如：写入/etc/dhcp/dhcpd.conf等

        defaults = {
            'interface': interface,
            'dhcp_range_start': range_start,
            'dhcp_range_end': range_end,
            'status': 'active',
        }
        if subnet is not None:
            defaults['subnet'] = subnet
        if gateway is not None:
            defaults['gateway'] = gateway
        pxe_server, created = PXEServerStatus.objects.update_or_create(
            server_ip=server_ip,
            defaults=defaults
        )
        return pxe_server

    @staticmethod
    def add_static_entry(mac: str, ip: str, hostname: str = None) -> WhiteList:
        """添加静态DHCP条目"""
        # TODO: 实现实际的静态条目添加逻辑

        entry, created = WhiteList.objects.update_or_create(
            mac_address=mac,
            defaults={
                'ip_address': ip,
                'hostname': hostname or '',
                'is_active': True,
            }
        )
        return entry

    @staticmethod
    def remove_static_entry(mac: str) -> bool:
        """移除静态DHCP条目"""
        try:
            entry = WhiteList.objects.get(mac_address=mac)
            entry.delete()
            return True
        except WhiteList.DoesNotExist:
            return False

    @staticmethod
    def list_static_entries(page: int = 1, page_size: int = 10):
        """获取静态条目列表"""
        queryset = WhiteList.objects.all()
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_pxe_server(server_ip: str = None) -> Optional[PXEServerStatus]:
        """获取PXE服务器信息"""
        try:
            if server_ip:
                return PXEServerStatus.objects.get(server_ip=server_ip)
            return PXEServerStatus.objects.filter(status='active').first()
        except PXEServerStatus.DoesNotExist:
            return None

    @staticmethod
    def list_pxe_servers(page: int = 1, page_size: int = 10):
        """获取PXE服务器列表"""
        queryset = PXEServerStatus.objects.all()
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """验证MAC地址格式"""
        import re
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """验证IP地址格式"""
        import re
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
