"""noVNC 远程安装服务"""
import logging
from typing import Dict

from backend.utils.ssh import SSHClient
from backend.common import HostConnectionError, OperationError

logger = logging.getLogger(__name__)


class NoVNCService:
    """noVNC 安装管理服务"""

    @staticmethod
    def install_novnc(config: Dict[str, str]) -> Dict[str, str]:
        """远程安装并启动 noVNC"""
        host = config.get("host")
        username = config.get("username")
        password = config.get("password")
        port = int(config.get("port", "22"))

        if not all([host, username, password]):
            raise OperationError("缺少主机连接信息")

        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            raise HostConnectionError(f"无法连接到主机 {host}")

        try:
            # 1. 检查网络连通性（在线/离线）
            stdout, stderr, exit_code = ssh.execute_command("ping -c 1 -W 2 mirrors.cucloud.cn >/dev/null 2>&1 && echo online || echo offline")
            is_online = "online" in stdout

            if is_online:
                # 在线安装依赖
                for pkg in ["tigervnc-server", "python3", "numpy", "expect"]:
                    stdout, stderr, exit_code = ssh.execute_command(f"rpm -qa | grep {pkg}")
                    if pkg not in stdout:
                        ssh.execute_command(f"yum install -y {pkg}")
            else:
                # 离线安装：检查本地包是否存在
                stdout, stderr, exit_code = ssh.execute_command("test -f /tmp/oskit/data/installnoVNC.tar.gz && echo exists || echo missing")
                if "missing" in stdout:
                    raise OperationError("离线安装缺少 installnoVNC.tar.gz 包")
                # 解压离线包
                ssh.execute_command("cd /tmp/oskit/data && tar -zxvf installnoVNC.tar.gz -C /tmp/")
                # 按架构安装离线 RPM
                stdout, _, _ = ssh.execute_command("uname -m")
                arch = stdout.strip()
                if "arm" in arch or "aarch64" in arch:
                    arch_dir = "arm"
                else:
                    arch_dir = "x86_64"

                for pkg_dir in ["tigervnc", "python3", "numpy", "expect"]:
                    rpm_dir = f"/tmp/installnoVNC/{pkg_dir}/{arch_dir}"
                    ssh.execute_command(f"cd {rpm_dir} && rpm -ivh *.rpm 2>/dev/null || true")

            # 2. 解压 noVNC（无论在线离线）
            ssh.execute_command("cd /tmp/oskit/data && tar -zxvf installnoVNC.tar.gz -C /tmp/ 2>/dev/null || true")

            # 3. 拷贝 generatePem.ctl 并生成 self.pem
            ssh.execute_command("mkdir -p /tmp/installnoVNC/noVNC/utils/")
            # 注：本地脚本路径需根据实际部署调整
            ssh.execute_command("test -f /usr/local/oskit/static/module/OSdeploy/novnc/generatePem.ctl && cp /usr/local/oskit/static/module/OSdeploy/novnc/generatePem.ctl /tmp/installnoVNC/noVNC/utils/ || true")
            ssh.execute_command("cd /tmp/installnoVNC/noVNC/utils && test -f generatePem.ctl && expect generatePem.ctl 2>/dev/null || true")

            # 4. 启动 tigervnc
            stdout, _, _ = ssh.execute_command("vncserver -list 2>/dev/null | grep ':1'")
            if ":1" not in stdout:
                ssh.execute_command("test -d /root/.vnc || mkdir -p /root/.vnc")
                ssh.execute_command("vncserver :1 2>/dev/null || true")
                # 如果启动失败，尝试 expect 脚本
                stdout, _, _ = ssh.execute_command("vncserver -list 2>/dev/null | grep ':1'")
                if ":1" not in stdout:
                    ssh.execute_command("test -f /usr/local/oskit/static/module/OSdeploy/novnc/startTigervnc.ctl && cp /usr/local/oskit/static/module/OSdeploy/novnc/startTigervnc.ctl /tmp/ || true")
                    ssh.execute_command("cd /tmp && test -f startTigervnc.ctl && expect startTigervnc.ctl 2>/dev/null || true")

            # 5. 启动 noVNC proxy
            novnc_dir = "/tmp/installnoVNC/noVNC/utils"
            ssh.execute_command(f"cd {novnc_dir} && nohup ./novnc_proxy --vnc 127.0.0.1:5901 --listen 6081 > novnc.log 2>&1 &")

            # 6. 验证 noVNC 是否启动成功
            stdout, _, _ = ssh.execute_command("curl -k -sI -w '%{http_code}' http://localhost:6081/vnc.html -o /dev/null 2>/dev/null")
            if "200" not in stdout:
                raise OperationError("noVNC 启动失败，HTTP 状态码非 200")

            # 7. 关闭防火墙（如运行中）
            stdout, _, _ = ssh.execute_command("systemctl status firewalld 2>/dev/null | grep 'active (running)'")
            if stdout.strip():
                ssh.execute_command("systemctl stop firewalld 2>/dev/null || true")

            return {"message": "noVNC 安装并启动成功"}

        finally:
            ssh.close()

    @staticmethod
    def close_novnc(config: Dict[str, str]) -> Dict[str, str]:
        """关闭 noVNC"""
        host = config.get("host")
        username = config.get("username")
        password = config.get("password")
        port = int(config.get("port", "22"))

        if not all([host, username, password]):
            raise OperationError("缺少主机连接信息")

        ssh = SSHClient(host=host, port=port, username=username, password=password, timeout=30)
        if not ssh.connect():
            raise HostConnectionError(f"无法连接到主机 {host}")

        try:
            # 1. 重启防火墙
            stdout, _, _ = ssh.execute_command("systemctl status firewalld 2>/dev/null | grep 'inactive'")
            if stdout.strip():
                ssh.execute_command("systemctl restart firewalld 2>/dev/null || true")

            # 2. 停止 noVNC
            ssh.execute_command("ps aux | grep 6081 | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")

            # 3. 停止 tigervnc
            stdout, _, _ = ssh.execute_command("vncserver -list 2>/dev/null | grep ':1'")
            if ":1" in stdout:
                ssh.execute_command("vncserver -kill :1 2>/dev/null || true")

            return {"message": "noVNC 已关闭"}

        finally:
            ssh.close()
