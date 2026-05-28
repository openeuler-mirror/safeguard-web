"""
Libvirt 客户端封装

提供 libvirt 连接、虚拟机 lifecycle 管理等功能
"""
import logging
from typing import Optional, Tuple, List, Dict

logger = logging.getLogger(__name__)

# libvirt 异常处理
LIBVIRT_NOT_FOUND = "Domain not found"
LIBVIRT_CONNECT_FAILED = "Failed to connect to libvirt"
LIBVIRT_OPERATION_FAILED = "Libvirt operation failed"


class LibvirtClient:
    """
    Libvirt 客户端封装

    用于连接远程 libvirt、虚拟机 lifecycle 管理等操作
    """

    def __init__(
        self,
        host: str,
        username: str = "root",
        password: Optional[str] = None,
        uri: Optional[str] = None,
    ):
        """
        初始化 Libvirt 客户端

        Args:
            host: 主机地址
            username: SSH 用户名（用于 qemu+ssh 连接）
            password: SSH 密码
            uri: libvirt URI（如果为空则使用 qemu+ssh://{username}@{host}/system）
        """
        self.host = host
        self.username = username
        self.password = password
        self._uri = uri or f"qemu+ssh://{username}@{host}/system"
        self._conn = None

    def _get_conn(self):
        """
        获取或创建 libvirt 连接

        Returns:
            libvirt connection
        """
        try:
            import libvirt
            if self._conn is None or not self._conn.is_alive():
                self._conn = libvirt.open(self._uri)
            return self._conn
        except Exception as e:
            logger.error(f"Failed to connect to libvirt at {self._uri}: {e}")
            raise

    def close(self):
        """关闭 libvirt 连接"""
        if self._conn:
            try:
                self._conn.close()
                self._conn = None
            except Exception as e:
                logger.error(f"Error closing libvirt connection: {e}")

    def lookup_domain_by_name(self, name: str):
        """
        根据名称查找域

        Args:
            name: 域名

        Returns:
            Domain 对象或 None
        """
        try:
            conn = self._get_conn()
            return conn.lookupByName(name)
        except Exception as e:
            logger.error(f"Failed to lookup domain {name}: {e}")
            return None

    def lookup_domain_by_uuid(self, uuid: str):
        """
        根据 UUID 查找域

        Args:
            uuid: 域 UUID

        Returns:
            Domain 对象或 None
        """
        try:
            conn = self._get_conn()
            return conn.lookupByUUIDString(uuid)
        except Exception as e:
            logger.error(f"Failed to lookup domain by UUID {uuid}: {e}")
            return None

    def domain_exists(self, name: str) -> bool:
        """检查域是否存在"""
        domain = self.lookup_domain_by_name(name)
        return domain is not None

    def get_domain_state(self, name: str) -> Optional[int]:
        """
        获取域状态

        Args:
            name: 域名

        Returns:
            域状态码（libvirt.VIR_DOMAIN_*）或 None
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return None
            return domain.state()[0]
        except Exception as e:
            logger.error(f"Failed to get domain state for {name}: {e}")
            return None

    def start_domain(self, name: str) -> Tuple[bool, str]:
        """
        启动域

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if domain.is_active():
                return True, f"Domain {name} is already running"

            domain.create()
            return True, f"Domain {name} started successfully"
        except Exception as e:
            logger.error(f"Failed to start domain {name}: {e}")
            return False, str(e)

    def stop_domain(self, name: str) -> Tuple[bool, str]:
        """
        停止域（强制关机）

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if not domain.is_active():
                return True, f"Domain {name} is not running"

            domain.destroy()
            return True, f"Domain {name} stopped successfully"
        except Exception as e:
            logger.error(f"Failed to stop domain {name}: {e}")
            return False, str(e)

    def shutdown_domain(self, name: str) -> Tuple[bool, str]:
        """
        关闭域（优雅关机）

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if not domain.is_active():
                return True, f"Domain {name} is not running"

            domain.shutdown()
            return True, f"Domain {name} shutdown signal sent"
        except Exception as e:
            logger.error(f"Failed to shutdown domain {name}: {e}")
            return False, str(e)

    def reboot_domain(self, name: str) -> Tuple[bool, str]:
        """
        重启域

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if not domain.is_active():
                return False, f"Domain {name} is not running"

            domain.reboot()
            return True, f"Domain {name} reboot signal sent"
        except Exception as e:
            logger.error(f"Failed to reboot domain {name}: {e}")
            return False, str(e)

    def pause_domain(self, name: str) -> Tuple[bool, str]:
        """
        暂停域

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if not domain.is_active():
                return False, f"Domain {name} is not running"

            domain.suspend()
            return True, f"Domain {name} paused successfully"
        except Exception as e:
            logger.error(f"Failed to pause domain {name}: {e}")
            return False, str(e)

    def resume_domain(self, name: str) -> Tuple[bool, str]:
        """
        恢复域

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            domain.resume()
            return True, f"Domain {name} resumed successfully"
        except Exception as e:
            logger.error(f"Failed to resume domain {name}: {e}")
            return False, str(e)

    def undefine_domain(self, name: str) -> Tuple[bool, str]:
        """
        删除域定义（必须先停止）

        Args:
            name: 域名

        Returns:
            (success, message) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            if domain.is_active():
                return False, f"Domain {name} is still running, please stop it first"

            domain.undefine()
            return True, f"Domain {name} undefined successfully"
        except Exception as e:
            logger.error(f"Failed to undefine domain {name}: {e}")
            return False, str(e)

    def define_domain_xml(self, xml: str) -> Tuple[bool, str, Optional[str]]:
        """
        定义域（从 XML）

        Args:
            xml: 域 XML 定义

        Returns:
            (success, message, domain_name) 元组
        """
        try:
            conn = self._get_conn()
            domain = conn.domainDefineXML(xml)
            domain_name = domain.name()
            return True, f"Domain {domain_name} defined successfully", domain_name
        except Exception as e:
            logger.error(f"Failed to define domain: {e}")
            return False, str(e), None

    def create_domain(self, xml: str) -> Tuple[bool, str]:
        """
        定义并创建域

        Args:
            xml: 域 XML 定义

        Returns:
            (success, message) 元组
        """
        try:
            conn = self._get_conn()
            domain = conn.domainDefineXML(xml)
            domain.create()
            return True, f"Domain {domain.name()} created and started"
        except Exception as e:
            logger.error(f"Failed to create domain: {e}")
            return False, str(e)

    def get_domain_xml(self, name: str) -> Optional[str]:
        """
        获取域的 XML 定义

        Args:
            name: 域名

        Returns:
            XML 字符串或 None
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return None
            return domain.XMLDesc(0)
        except Exception as e:
            logger.error(f"Failed to get domain XML for {name}: {e}")
            return None

    def qemu_agent_command(self, name: str, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        通过 qemu-guest-agent 执行命令

        Args:
            name: 域名
            command: JSON 格式的 QMP 命令
            timeout: 超时时间（秒）

        Returns:
            (success, output) 元组
        """
        try:
            domain = self.lookup_domain_by_name(name)
            if domain is None:
                return False, f"Domain {name} not found"

            result = domain.qemuAgentCommand(command, timeout, 0)
            return True, result
        except Exception as e:
            logger.error(f"Failed to execute qemu-agent command on {name}: {e}")
            return False, str(e)

    def list_all_domains(self) -> List[Dict]:
        """
        列出所有域

        Returns:
            域信息列表
        """
        try:
            conn = self._get_conn()
            domains = conn.listAllDomains()
            result = []
            for d in domains:
                state, _ = d.state()
                result.append({
                    'name': d.name(),
                    'uuid': d.UUIDString(),
                    'state': state,
                    'id': d.ID() if state == 1 else -1,
                })
            return result
        except Exception as e:
            logger.error(f"Failed to list domains: {e}")
            return []

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False

    def __del__(self):
        """析构函数确保连接关闭"""
        self.close()