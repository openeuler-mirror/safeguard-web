"""Sensor 部署服务"""
import logging
import os
import uuid
from typing import Dict, Any

import toml

from backend.utils.ssh import SSHClient

logger = logging.getLogger(__name__)


class SensorService:
    """Sensor 部署管理服务"""

    @staticmethod
    def install_sensor(config: Dict[str, Any]) -> Dict[str, Any]:
        """远程安装 sensor RPM 包

        Args:
            config: 包含 host, username, password, port, base_path 等

        Returns:
            {"job_id": str, "status": str, "message": str}
        """
        host = config.get("host")
        username = config.get("username")
        password = config.get("password")
        port = int(config.get("port", "22"))
        base_path = config.get("base_path", "/opt/sensor/rpms")

        job_id = f"sensor-{uuid.uuid4().hex[:8]}"

        ssh = SSHClient(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=30,
        )
        if not ssh.connect():
            return {"job_id": job_id, "status": "failed", "message": f"无法连接到主机 {host}"}

        try:
            # 1. 获取系统版本
            stdout, stderr, exit_code = ssh.execute_command("cat /etc/os-release")
            if exit_code != 0:
                return {"job_id": job_id, "status": "failed", "message": f"获取系统版本失败: {stderr}"}

            os_release = stdout.lower()
            if '"7"' in os_release and "centos" in os_release:
                os_type = "el7"
            elif '"9"' in os_release and "centos" in os_release:
                os_type = "el9"
            elif '"3.0"' in os_release and "culinux" in os_release:
                os_type = "ule3"
            else:
                return {"job_id": job_id, "status": "failed", "message": f"不支持的系统类型: {stdout}"}

            # 2. 获取架构
            stdout, stderr, exit_code = ssh.execute_command("uname -m")
            if exit_code != 0:
                return {"job_id": job_id, "status": "failed", "message": f"获取架构失败: {stderr}"}

            arch = stdout.strip()
            # 统一架构命名
            if arch == "x86_64":
                arch_rpm = "x86_64"
            elif arch in ("aarch64", "arm64"):
                arch_rpm = "aarch64"
            else:
                return {"job_id": job_id, "status": "failed", "message": f"不支持的架构: {arch}"}

            # 3. 查找并安装 RPM
            rpm_pattern = f"sensor-*.{os_type}.{arch_rpm}.rpm"
            rpm_cmd = f"find {base_path} -name '{rpm_pattern}' | head -n 1"
            stdout, stderr, exit_code = ssh.execute_command(rpm_cmd)
            if exit_code != 0 or not stdout.strip():
                return {"job_id": job_id, "status": "failed",
                        "message": f"未找到 RPM 包: {rpm_pattern} in {base_path}"}

            rpm_file = stdout.strip()
            install_cmd = f"yum install -y {rpm_file} || rpm -ivh {rpm_file}"
            stdout, stderr, exit_code = ssh.execute_command(install_cmd)
            if exit_code != 0:
                return {"job_id": job_id, "status": "failed",
                        "message": f"安装失败: {stderr}"}

            return {"job_id": job_id, "status": "success", "message": f"Sensor 安装成功: {rpm_file}"}

        finally:
            ssh.close()

    @staticmethod
    def update_config(serial_number: str, override_config: Dict[str, Any],
                      host_info: Dict[str, str]) -> Dict[str, Any]:
        """更新 sensor 配置文件并重启服务

        Args:
            serial_number: 主机序列号
            override_config: 需要覆盖的配置项
            host_info: 包含 host, username, password, port

        Returns:
            {"status": str, "config": dict, "message": str}
        """
        host = host_info.get("host")
        username = host_info.get("username")
        password = host_info.get("password")
        port = int(host_info.get("port", "22"))

        ssh = SSHClient(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=30,
        )
        if not ssh.connect():
            return {"status": "failed", "message": f"无法连接到主机 {host}"}

        try:
            # 1. 读取现有配置（或模板）
            template_path = "/opt/sensor/template/config.toml"
            output_path = "/opt/sensor/config.toml"

            stdout, stderr, exit_code = ssh.execute_command(
                f"test -f {output_path} && cat {output_path} || cat {template_path}"
            )
            if exit_code != 0:
                return {"status": "failed", "message": f"读取配置失败: {stderr}"}

            try:
                base_config = toml.loads(stdout)
            except toml.TomlDecodeError as e:
                return {"status": "failed", "message": f"解析 TOML 失败: {e}"}

            # 2. 递归合并配置
            merged = SensorService._merge_configs(base_config, override_config)

            # 3. 生成新配置并写入
            new_toml = toml.dumps(merged)
            # 使用 heredoc 写入远程文件
            escaped = new_toml.replace("'", "'\"'\"'")
            cmd = f"cat > {output_path} << 'EOF_TOML'\n{escaped}\nEOF_TOML"
            stdout, stderr, exit_code = ssh.execute_command(cmd)
            if exit_code != 0:
                return {"status": "failed", "message": f"写入配置失败: {stderr}"}

            # 4. 重启 sensor 服务
            stdout, stderr, exit_code = ssh.execute_command("systemctl restart sensor")
            if exit_code != 0:
                return {"status": "failed", "message": f"重启服务失败: {stderr}"}

            return {"status": "success", "config": merged, "message": "配置更新并重启成功"}

        finally:
            ssh.close()

    @staticmethod
    def operate_sensor(config: Dict[str, Any], operate: str) -> Dict[str, Any]:
        """操作 sensor 服务

        Args:
            config: 包含 host, username, password, port
            operate: start / stop / restart / delete

        Returns:
            {"status": str, "output": str, "message": str}
        """
        valid = {"start", "stop", "restart", "delete"}
        if operate not in valid:
            return {"status": "failed", "message": f"无效操作: {operate}, 支持 {valid}"}

        host = config.get("host")
        username = config.get("username")
        password = config.get("password")
        port = int(config.get("port", "22"))

        ssh = SSHClient(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=30,
        )
        if not ssh.connect():
            return {"status": "failed", "message": f"无法连接到主机 {host}"}

        try:
            if operate == "delete":
                command = (
                    "systemctl stop sensor && systemctl disable sensor && "
                    "rm -f /etc/systemd/system/sensor.service && systemctl daemon-reload"
                )
            else:
                command = f"systemctl {operate} sensor"

            stdout, stderr, exit_code = ssh.execute_command(command)
            output = stdout if stdout else stderr

            if exit_code != 0:
                return {"status": "failed", "output": output, "message": f"操作失败: {stderr}"}

            return {"status": "success", "output": output, "message": f"sensor {operate} 成功"}

        finally:
            ssh.close()

    @staticmethod
    def _merge_configs(base: Any, override: Any) -> Any:
        """递归合并两个字典"""
        if not isinstance(base, dict) or not isinstance(override, dict):
            return override
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = SensorService._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
