"""
远程主机命令执行统一接口

提供简化的远程命令执行方法，供 Host、VM、Safeguard 等模块复用
"""
from typing import Tuple
from backend.utils.ssh import SSHClient


def remote_host_command(
    host: str,
    port: int,
    username: str,
    password: str,
    command: str,
    timeout: int = 10,
) -> Tuple[str, str]:
    """
    远程执行命令的简明接口

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        command: 要执行的命令
        timeout: 超时时间（秒）

    Returns:
        (stdout, stderr) 元组
    """
    with SSHClient(host, port, username, password, timeout) as client:
        stdout, stderr, exit_code = client.execute_command(command)
        return stdout, stderr


def remote_dir_exist(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
) -> bool:
    """
    检查远程目录是否存在

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        path: 目录路径

    Returns:
        目录是否存在
    """
    with SSHClient(host, port, username, password) as client:
        return client.dir_exists(path)


def remote_file_exist(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
) -> bool:
    """
    检查远程文件是否存在

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        path: 文件路径

    Returns:
        文件是否存在
    """
    with SSHClient(host, port, username, password) as client:
        return client.file_exists(path)


def remote_create_dir(
    host: str,
    port: int,
    username: str,
    password: str,
    path: str,
    recursive: bool = True,
) -> bool:
    """
    在远程主机上创建目录

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        path: 目录路径
        recursive: 是否递归创建

    Returns:
        创建是否成功
    """
    with SSHClient(host, port, username, password) as client:
        if recursive:
            return client.create_dir_recursive(path)
        return client.create_dir(path)


def remote_file_exists(
    host: str,
    port: int,
    username: str,
    password: str,
    remote_dir: str,
    filename: str,
) -> bool:
    """
    检查远程目录中是否存在指定文件

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        remote_dir: 远程目录
        filename: 文件名

    Returns:
        文件是否存在
    """
    import os
    file_path = os.path.join(remote_dir, filename)
    return remote_file_exist(host, port, username, password, file_path)


def remote_dir_exists(
    host: str,
    port: int,
    username: str,
    password: str,
    remote_dir: str,
) -> bool:
    """
    检查远程目录是否存在（带路径拼接）

    Args:
        host: 主机地址
        port: SSH 端口
        username: 用户名
        password: 密码
        remote_dir: 远程目录

    Returns:
        目录是否存在
    """
    return remote_dir_exist(host, port, username, password, remote_dir)


def local_host_command(command: str) -> Tuple[str, str]:
    """
    在本地执行命令

    Args:
        command: 要执行的命令

    Returns:
        (stdout, stderr) 元组
    """
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)


def local_dir_exist(path: str) -> Tuple[bool, str]:
    """
    检查本地目录是否存在

    Args:
        path: 目录路径

    Returns:
        (是否存在, 错误信息)
    """
    import os
    if os.path.isdir(path):
        return True, ""
    return False, f"Directory does not exist: {path}"


def local_file_exist(directory: str, filename: str) -> Tuple[bool, str]:
    """
    检查本地目录中是否存在指定文件

    Args:
        directory: 目录路径
        filename: 文件名

    Returns:
        (是否存在, 错误信息)
    """
    import os
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        return True, ""
    return False, f"File does not exist: {file_path}"