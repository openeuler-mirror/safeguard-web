"""RPC 文件操作服务"""
import logging
from typing import Tuple
from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)


class FileService:
    """文件操作服务"""

    @staticmethod
    def file_copy(srcfile: str, destfile: str, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        将本地文件复制到远程主机

        Returns:
            (success, message) 元组
        """
        try:
            with SSHClient(host, port, username, password) as client:
                ok = client.upload_file(srcfile, destfile)
                if ok:
                    return True, f"File copied successfully: {srcfile} -> {destfile}"
                return False, f"File copy failed: {srcfile} -> {destfile}"
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return False, str(e)

    @staticmethod
    def file_download(remote_path: str, local_path: str, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        从远程主机下载文件

        Returns:
            (success, message) 元组
        """
        try:
            with SSHClient(host, port, username, password) as client:
                ok = client.download_file(remote_path, local_path)
                if ok:
                    return True, f"File downloaded successfully: {remote_path} -> {local_path}"
                return False, f"File download failed: {remote_path} -> {local_path}"
        except Exception as e:
            logger.error(f"File download failed: {e}")
            return False, str(e)

    @staticmethod
    def remote_file_exists(remote_path: str, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        检查远程文件是否存在

        Returns:
            (exists, message) 元组
        """
        try:
            with SSHClient(host, port, username, password) as client:
                exists = client.file_exists(remote_path)
                return exists, ""
        except Exception as e:
            return False, str(e)
