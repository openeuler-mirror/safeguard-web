"""
SSH 客户端封装

提供 SSH 连接、远程命令执行、文件传输等功能
"""
import paramiko
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SSHClient:
    """
    SSH 客户端封装

    用于远程主机连接、命令执行、文件传输等操作
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 10,
        key_filename: Optional[str] = None,
    ):
        """
        初始化 SSH 客户端

        Args:
            host: 主机地址
            port: SSH 端口
            username: 用户名
            password: 密码
            timeout: 连接超时时间（秒）
            key_filename: 私钥文件路径（可选）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.key_filename = key_filename
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        """
        建立 SSH 连接

        Returns:
            连接是否成功
        """
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'username': self.username,
                'timeout': self.timeout,
            }

            if self.key_filename:
                connect_kwargs['key_filename'] = self.key_filename
            else:
                connect_kwargs['password'] = self.password

            self._client.connect(**connect_kwargs)
            logger.info(f"SSH connection established to {self.host}:{self.port}")
            return True
        except paramiko.SSHException as e:
            logger.error(f"SSH connection failed to {self.host}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.host}:{self.port}: {e}")
            return False

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        执行远程命令

        Args:
            command: 要执行的命令

        Returns:
            (stdout, stderr, exit_code) 元组
        """
        if not self._client:
            if not self.connect():
                return "", "Connection not established", -1

        try:
            stdin, stdout, stderr = self._client.exec_command(command, timeout=self.timeout)
            exit_code = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8', errors='replace')
            stderr_text = stderr.read().decode('utf-8', errors='replace')
            return stdout_text, stderr_text, exit_code
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return "", str(e), -1

    def file_exists(self, remote_path: str) -> bool:
        """
        检查远程文件是否存在

        Args:
            remote_path: 远程文件路径

        Returns:
            文件是否存在
        """
        if not self._client:
            return False

        try:
            sftp = self._client.open_sftp()
            sftp.stat(remote_path)
            sftp.close()
            return True
        except IOError:
            return False
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False

    def dir_exists(self, remote_path: str) -> bool:
        """
        检查远程目录是否存在

        Args:
            remote_path: 远程目录路径

        Returns:
            目录是否存在
        """
        if not self._client:
            return False

        try:
            sftp = self._client.open_sftp()
            sftp.stat(remote_path)
            sftp.close()
            return True
        except IOError:
            return False
        except Exception as e:
            logger.error(f"Error checking directory existence: {e}")
            return False

    def create_dir(self, remote_path: str) -> bool:
        """
        创建远程目录

        Args:
            remote_path: 远程目录路径

        Returns:
            创建是否成功
        """
        if not self._client:
            return False

        try:
            sftp = self._client.open_sftp()
            sftp.mkdir(remote_path)
            sftp.close()
            logger.info(f"Directory created: {remote_path}")
            return True
        except IOError as e:
            if "File exists" in str(e):
                logger.info(f"Directory already exists: {remote_path}")
                return True
            logger.error(f"Failed to create directory {remote_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create directory {remote_path}: {e}")
            return False

    def create_dir_recursive(self, remote_path: str) -> bool:
        """
        递归创建远程目录

        Args:
            remote_path: 远程目录路径

        Returns:
            创建是否成功
        """
        if not self._client:
            return False

        if self.dir_exists(remote_path):
            return True

        parent = remote_path.rsplit('/', 1)[0]
        if parent and parent != '/' and not self.dir_exists(parent):
            if not self.create_dir_recursive(parent):
                return False

        return self.create_dir(remote_path)

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        下载远程文件到本地

        Args:
            remote_path: 远程文件路径
            local_path: 本地保存路径

        Returns:
            下载是否成功
        """
        if not self._client:
            return False

        try:
            sftp = self._client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            logger.info(f"File downloaded: {remote_path} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file {remote_path}: {e}")
            return False

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        上传本地文件到远程

        Args:
            local_path: 本地文件路径
            remote_path: 远程保存路径

        Returns:
            上传是否成功
        """
        if not self._client:
            return False

        try:
            sftp = self._client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info(f"File uploaded: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file {local_path}: {e}")
            return False

    def close(self):
        """
        关闭 SSH 连接
        """
        try:
            if self._client:
                self._client.close()
                self._client = None
            logger.info(f"SSH connection closed: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Error closing SSH connection: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False

    def __del__(self):
        """析构函数确保连接关闭"""
        self.close()

def remote_host_command(host, port, username, password, command, timeout=60):
    """在远程主机上执行命令（便捷函数）"""
    with SSHClient(host, port, username, password, timeout=timeout) as client:
        stdout, stderr, exit_code = client.execute_command(command)
        output = stdout if stdout else stderr
        return output, exit_code


def remote_package_install(host, port, username, password, package, timeout=300):
    """在远程主机上安装软件包（便捷函数）"""
    return remote_host_command(host, port, username, password, f"yum install -y {package}", timeout=timeout)


def file_copy(srcfile, destfile, host, port, username, password):
    """将本地文件复制到远程主机（便捷函数）"""
    with SSHClient(host, port, username, password) as client:
        return client.upload_file(srcfile, destfile)


def remote_file_exist(host, port, username, password, dirname, filename):
    """检查远程主机上的文件是否存在"""
    with SSHClient(host, port, username, password) as client:
        try:
            import os as _os
            path = _os.path.join(dirname, filename)
            exists = client.file_exists(path)
            return exists, ""
        except Exception as e:
            return False, str(e)


def remote_ping_host(host, port, username, password, target, timeout=10):
    """通过远程主机 ping 目标地址"""
    with SSHClient(host, port, username, password, timeout=timeout) as client:
        stdout, stderr, exit_code = client.execute_command(f"ping -c 1 -W 3 {target}")
        output = stdout if stdout else stderr
        return exit_code == 0, output


def local_ping_host(host, timeout=5):
    """本地 ping 目标地址"""
    try:
        import subprocess as _subprocess
        result = _subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        output = result.stdout if result.stdout else result.stderr
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)
