"""OSmigrate x2cu 系统迁移服务"""
import os
import re
import json
import time
from typing import List, Dict, Optional
from backend.utils.ssh import (
    SSHClient,
    remote_host_command,
    remote_package_install,
    file_copy,
    remote_file_exist,
    remote_ping_host,
    local_ping_host,
)
from backend.services.task import TaskService
from backend.models.osmigrate.migrate_job import MigrateJob
import logging

logger = logging.getLogger(__name__)


class HostInfo:
    """主机信息结构"""
    def __init__(self, host: str, port: str = "22", username: str = "", password: str = ""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def to_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            host=data.get("host", ""),
            port=data.get("port", "22"),
            username=data.get("username", ""),
            password=data.get("password", ""),
        )


class X2cuService:
    """x2cu 系统迁移服务"""

    @staticmethod
    def _create_migrate_job(job_type: str, target_host: str, migrate_type: str = "", hosts: list = None) -> str:
        """创建迁移任务记录"""
        job_id = TaskService.generate_job_id(f"migrate-{job_type}")
        MigrateJob.objects.create(
            job_id=job_id,
            job_type=job_type,
            target_host=target_host,
            migrate_type=migrate_type,
            hosts_json=hosts or [],
            status="pending",
            progress=0,
        )
        return job_id

    @staticmethod
    def _update_migrate_job(job_id: str, status: str = None, progress: int = None, error_message: str = None, result: dict = None):
        """更新迁移任务状态"""
        try:
            job = MigrateJob.objects.get(job_id=job_id)
            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = progress
            if error_message is not None:
                job.error_message = error_message
            if result is not None:
                job.result = result
            job.save()
        except MigrateJob.DoesNotExist:
            logger.warning(f"MigrateJob not found: {job_id}")

    # ---------- 基础迁移操作 ----------

    @staticmethod
    def migrate_init(host: str, port: str, username: str, password: str) -> None:
        """
        迁移初始化：安装 x2cu 工具、下载 culinux.tar.gz
        对应原始 Go 代码: OSmigrate.MigrateInit
        """
        hostport = f"{host}:{port}"
        port_int = int(port) if port else 22

        # 检查网络连通性
        res, _ = remote_ping_host(host, port_int, username, password, "mirrors.cucloud.cn")
        if not res:
            res, _ = remote_ping_host(host, port_int, username, password, "173.20.3.2")
            if res:
                cmdline = "echo '173.20.3.2 mirrors.cucloud.cn' >> /etc/hosts"
                output, exit_code = remote_host_command(host, port_int, username, password, cmdline)
                if exit_code != 0:
                    raise Exception(f"migrate init fail: {output}")
            else:
                # 离线环境，使用 rpm 安装迁移工具
                output, exit_code = remote_host_command(host, port_int, username, password, "rpm -qa | grep x2cu")
                if "x2cu" not in output:
                    exists, err = remote_file_exist(host, port_int, username, password, "/tmp/oskit/data/migrate/", "migrate-data.tar.gz")
                    if not exists:
                        raise Exception(f"migrate init fail, file not exist: {err}")

                    cmdline = "tar -zxvf /tmp/oskit/data/migrate/migrate-data.tar.gz -C /tmp"
                    output, exit_code = remote_host_command(host, port_int, username, password, cmdline)
                    if exit_code != 0:
                        raise Exception(f"migrate init fail, uncompress fail: {output}")

                    arch, _ = remote_host_command(host, port_int, username, password, "uname -m")
                    arch = arch.strip()
                    if "arm" in arch:
                        arch = "arm"

                    # 安装 rsync
                    exitout, _ = remote_host_command(host, port_int, username, password, "rpm -qa | grep rsync")
                    if "rsync" not in exitout:
                        rsync_dir = f"/tmp/migrate-data/rsync/{arch}"
                        script_cmd = f"cd {rsync_dir} && rpm -ivh rsync*.rpm"
                        output, exit_code = remote_host_command(host, port_int, username, password, script_cmd)
                        if exit_code != 0:
                            raise Exception(f"migrate init fail, rpm rsync fail: {output}")
                        exitout, _ = remote_host_command(host, port_int, username, password, "rpm -qa | grep rsync")
                        if "rsync" not in exitout:
                            raise Exception(f"migrate init fail, rpm rsync fail: {exitout}")

                    other_dir = f"/tmp/migrate-data/other/{arch}"
                    script_cmd = f"cd {other_dir} && rpm --replacepkgs -Uvh *.rpm"
                    output, exit_code = remote_host_command(host, port_int, username, password, script_cmd)
                    if exit_code != 0:
                        raise Exception(f"migrate init fail, install other and x2cu rpm fail: {output}")

                    exitout, _ = remote_host_command(host, port_int, username, password, "rpm -qa | grep x2cu")
                    if "x2cu" not in exitout:
                        raise Exception(f"migrate init fail, rpm x2cu fail: {exitout}")

                # 检查 culinux.tar.gz
                output, _ = remote_host_command(host, port_int, username, password, "ls /tmp")
                if "culinux.tar.gz" not in output:
                    raise Exception(f"migrate init fail, file culinux.tar.gz not exist: {output}")
                return

        # 在线环境：使用 yum 安装
        output, exit_code = remote_package_install(host, port_int, username, password, "wget")
        if exit_code != 0:
            raise Exception(f"migrate init fail: {output}")

        output, _ = remote_host_command(host, port_int, username, password, "rpm -qa | grep x2cu")
        if "x2cu" not in output:
            output, _ = remote_host_command(host, port_int, username, password, "yum repolist")
            if "cueps-cutools" not in output:
                cmdline = "wget -P /etc/yum.repos.d/ https://mirrors.cucloud.cn/cueps/3.0/cueps-cutools.repo"
                output, exit_code = remote_host_command(host, port_int, username, password, cmdline)
                if exit_code != 0:
                    raise Exception(f"migrate init fail: {output}")

            output, exit_code = remote_package_install(host, port_int, username, password, "x2cu")
            if exit_code != 0:
                raise Exception(f"migrate init fail: {output}")

        output, _ = remote_host_command(host, port_int, username, password, "ls /tmp")
        if "culinux.tar.gz" not in output:
            cmdline = "wget -P /tmp https://mirrors.cucloud.cn/culinux/oem/x2cu/culinux.tar.gz"
            output, exit_code = remote_host_command(host, port_int, username, password, cmdline)
            if exit_code != 0:
                raise Exception(f"migrate init fail: {output}")

    @staticmethod
    def migrate_core(host: str, port: str, username: str, password: str, datafile: str = "") -> None:
        """
        执行迁移核心命令
        对应原始 Go 代码: OSmigrate.MigrateCore
        """
        if not datafile:
            datafile = "/tmp/culinux.tar.gz"
        port_int = int(port) if port else 22
        cmdline = f"x2cu {datafile} >>/tmp/migrate.log 2>&1"
        output, exit_code = remote_host_command(host, port_int, username, password, cmdline, timeout=600)
        if exit_code != 0:
            raise Exception(f"migrate fail: {output}")

    @staticmethod
    def migrate_back(host: str, port: str, username: str, password: str) -> None:
        """
        执行迁移回滚
        对应原始 Go 代码: OSmigrate.MigrateBack
        """
        port_int = int(port) if port else 22
        cmdline = "yes | cu2x >>/tmp/migrateback.log 2>&1"
        output, exit_code = remote_host_command(host, port_int, username, password, cmdline, timeout=600)
        if exit_code != 0:
            raise Exception(f"migrate back fail: {output}")

    # ---------- 云管特殊迁移 ----------

    @staticmethod
    def migrate_init4_yunguan_portal1(host: str, port: str, username: str, password: str, redis_passwd: str) -> None:
        """云管 Portal1 初始化"""
        port_int = int(port) if port else 22
        hostport = f"{host}:{port}"

        srcfile = "/usr/local/oskit/static/migrate/cu-portal-deploy.tar.gz"
        destfile = "/data"
        if os.path.exists(srcfile):
            ok = file_copy(srcfile, destfile, host, port_int, username, password)
            if not ok:
                raise Exception("migrate init fail, scp portal_init1.sh to node1 fail")

        cmds = [
            "tar -zxf /data/cu-portal-deploy.tar.gz -C /data",
            "cp /data/cu-portal-deploy/portal_init1.sh /etc/x2cu/init.d/",
            f"redis-cli -p 16379 -a {redis_passwd} save",
            f"redis-cli -p 16379 -a {redis_passwd} config get dir",
        ]
        for cmd in cmds:
            output, exit_code = remote_host_command(host, port_int, username, password, cmd)
            if exit_code != 0:
                raise Exception(f"migrate init fail, cmd fail: {cmd}, output: {output}")

        # 处理 redis dir
        redis_res = output
        redis_dir = X2cuService._redis_dir_collect(redis_res)
        if not redis_dir:
            raise Exception("migrate init fail, redis dir collect fail")

        copy_cmd = f"cp {redis_dir}/appendonly.aof {redis_dir}/dump.rdb /root/deploy/redis"
        output, exit_code = remote_host_command(host, port_int, username, password, copy_cmd)
        if exit_code != 0:
            raise Exception(f"migrate init fail, node1 redis data directory copy fail: {output}")

        X2cuService._x2cu_json_handle()

    @staticmethod
    def migrate_post4_yunguan_portal1(host: str, port: str, username: str, password: str) -> None:
        """云管 Portal1 后置处理"""
        port_int = int(port) if port else 22
        output, exit_code = remote_host_command(host, port_int, username, password, "kubectl get po -n msp-prod")
        if exit_code != 0:
            raise Exception(f"migrate post fail, node1 kubectl exec fail: {output}")
        if "Running" not in output:
            cmdlines = [
                "cd /data/helm",
                "helm delete coms-ms-obsauthservice -n msp-prod",
                "helm delete msp-middleware -n msp-prod",
                "helm install msp-middleware msp-middleware -n msp-prod",
                "helm install coms-ms-obsauthservice coms-ms-obsauthservice -n msp-prod",
            ]
            for cmdline in cmdlines:
                output, exit_code = remote_host_command(host, port_int, username, password, cmdline)
                if exit_code != 0:
                    raise Exception(f"migrate post fail, node1 exec cmdline {cmdline} fail: {output}")

        output, _ = remote_host_command(host, port_int, username, password, "kubectl get po -n msp-prod")
        if "Running" not in output:
            raise Exception("migrate post fail, node1 k8s pod status error")

        output, _ = remote_host_command(host, port_int, username, password,
            "kubectl exec -it osh-control-openstack-rabbitmq-rabbitmq-0 -n openstack -- rabbitmqctl list_users|grep msp-wocloud")
        if "msp-wocloud" in output:
            output, exit_code = remote_host_command(host, port_int, username, password, "sh /data/cu-portal-deploy/start-service1.sh")
            if exit_code != 0:
                raise Exception(f"migrate post fail, node1 exec start-service1.sh: {output}")
        else:
            cmds = [
                "sh /data/cu-portal-deploy/install-k8s-rabbitmq.sh",
                "sh /data/cu-portal-deploy/start-service1.sh",
            ]
            for cmd in cmds:
                output, exit_code = remote_host_command(host, port_int, username, password, cmd)
                if exit_code != 0:
                    raise Exception(f"migrate post fail, node1 exec {cmd}: {output}")

    @staticmethod
    def migrate_init4_yunguan_portal2(host: str, port: str, username: str, password: str) -> None:
        """云管 Portal2 初始化"""
        port_int = int(port) if port else 22
        srcfile = "/usr/local/oskit/static/migrate/cu-portal-deploy.tar.gz"
        destfile = "/data"
        if os.path.exists(srcfile):
            ok = file_copy(srcfile, destfile, host, port_int, username, password)
            if not ok:
                raise Exception("migrate init fail, scp portal_init1.sh to node2 fail")

        cmds = [
            "tar -zxf /data/cu-portal-deploy.tar.gz -C /data",
            "cp /data/cu-portal-deploy/portal_init1.sh /etc/x2cu/init.d/",
        ]
        for cmd in cmds:
            output, exit_code = remote_host_command(host, port_int, username, password, cmd)
            if exit_code != 0:
                raise Exception(f"migrate init fail: {cmd}, output: {output}")

    @staticmethod
    def migrate_post4_yunguan_portal2(host: str, port: str, username: str, password: str) -> None:
        """云管 Portal2 后置处理"""
        port_int = int(port) if port else 22
        output, exit_code = remote_host_command(host, port_int, username, password, "sh /data/cu-portal-deploy/start-service2.sh")
        if exit_code != 0:
            raise Exception(f"migrate post fail, node2 exec start-service2.sh: {output}")

    @staticmethod
    def migrate_init4_yunguan_monitor(host01: HostInfo, host02: HostInfo, host03: HostInfo) -> None:
        """云管监控初始化"""
        # 配置免密 SSH
        # ...（简化实现）
        hosts = [host01, host02, host03]
        for host in hosts:
            port_int = int(host.port) if host.port else 22
            srcfiles = [
                ("/usr/local/oskit/static/migrate/x2cu/yg/monitor/config.json", "/etc/x2cu/config.json"),
                ("/usr/local/oskit/static/migrate/x2cu/yg/monitor/101-init.sh", "/etc/x2cu/post.d/101-init.sh"),
                ("/usr/local/oskit/static/migrate/x2cu/yg/monitor/stop-monitor.sh", "/tmp/stop-monitor.sh"),
            ]
            for src, dest in srcfiles:
                if os.path.exists(src):
                    ok = file_copy(src, dest, host.host, port_int, host.username, host.password)
                    if not ok:
                        raise Exception(f"migrate init fail for yunguan Monitor, copy {src} fail")

            output, exit_code = remote_host_command(host.host, port_int, host.username, host.password, "sh /data/cu-monitor-deploy/stop-monitor.sh")
            if exit_code != 0:
                raise Exception(f"migrate init fail for yunguan Monitor, exec stop-monitor.sh fail: {output}")

    @staticmethod
    def migrate_post4_yunguan_monitor(host01: HostInfo, host02: HostInfo, host03: HostInfo) -> None:
        """云管监控后置处理"""
        hosts = [host01, host02, host03]
        mongo_db_cmdlines = [
            "mongod --quiet -f /etc/mongodb/config.conf --fork --wiredTigerCacheSizeGB 1",
            "mongod --quiet -f /etc/mongodb/shard1.conf --fork --wiredTigerCacheSizeGB 1",
            "mongod --quiet -f /etc/mongodb/shard2.conf --fork --wiredTigerCacheSizeGB 1",
            "mongod --quiet -f /etc/mongodb/shard3.conf --fork --wiredTigerCacheSizeGB 1",
            "mongos -f /etc/mongodb/mongos.conf",
        ]
        for host_index, host in enumerate(hosts):
            port_int = int(host.port) if host.port else 22
            for cmd in mongo_db_cmdlines:
                output, exit_code = remote_host_command(host.host, port_int, host.username, host.password, cmd)
                if exit_code != 0:
                    raise Exception(f"migrate post fail for yunguan Monitor, exec mongodb cmd: {cmd} fail: {output}")
            if host_index == 1:
                output, exit_code = remote_host_command(host.host, port_int, host.username, host.password, "start-all.sh")
                if exit_code != 0:
                    raise Exception(f"migrate post fail for yunguan Monitor, exec start-all.sh fail: {output}")

            zk_cmd = "/opt/zookeeper/bin/zkServer.sh start"
            output, exit_code = remote_host_command(host.host, port_int, host.username, host.password, zk_cmd)
            if exit_code != 0:
                raise Exception(f"migrate post fail for yunguan Monitor, start zk fail: {output}")

            kafka_cmd = "nohup kafka-server-start.sh /opt/kafka/config/server.properties 2>&1 &"
            output, exit_code = remote_host_command(host.host, port_int, host.username, host.password, kafka_cmd)
            if exit_code != 0:
                raise Exception(f"migrate post fail for yunguan Monitor, start kafka fail: {output}")

        # host02 adapter
        port_int2 = int(host02.port) if host02.port else 22
        output, exit_code = remote_host_command(host02.host, port_int2, host02.username, host02.password, "sh /opt/adapter/start.sh")
        if exit_code != 0:
            raise Exception(f"migrate post fail for yunguan Monitor2, start monitor adapter fail: {output}")

        # host03 monitor
        port_int3 = int(host03.port) if host03.port else 22
        cmdlines = [
            "sh /opt/monitor/start_cloudhost.sh",
            "sh /opt/monitor/start_other.sh",
            "sh /opt/monitor/start_csk.sh",
            "sh /opt/alarm/start.sh",
        ]
        for cmd in cmdlines:
            output, exit_code = remote_host_command(host03.host, port_int3, host03.username, host03.password, cmd)
            if exit_code != 0:
                raise Exception(f"migrate post fail for yunguan Monitor3 fail: {output}")

    # ---------- 工具方法 ----------

    @staticmethod
    def _redis_dir_collect(text: str) -> str:
        """从 redis config get dir 输出中提取目录"""
        regex = re.compile(r'"(.*?)"')
        matches = regex.findall(text)
        res = []
        for item in matches:
            if item == "/root/deploy/redis":
                continue
            if item.startswith("/"):
                res.append(item)
        if len(res) > 1:
            raise Exception("redis dir nums gt 1")
        return res[0] if res else ""

    @staticmethod
    def _x2cu_json_handle() -> None:
        """处理 x2cu config.json"""
        try:
            with open("/etc/x2cu/config.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            raise Exception(f"failed to read file: {e}")

        new_values = [
            "/root/deploy/redis/",
            "/root/deploy/check_service.sh",
            "/usr/local/java/",
            "/etc/redis.conf",
            "/usr/local/bin/",
            "/home/wocloud/canal/",
            "/etc/profile",
        ]
        copy_list = data.get("copylist", [])
        for value in new_values:
            copy_list.append(value)
        data["copylist"] = copy_list

        with open("/tmp/tmp.json", "w") as f:
            json.dump(data, f, indent=2)

    # ---------- 对外业务接口 ----------

    @staticmethod
    def start_migrate_init(
        host: str,
        port: str,
        username: str,
        password: str,
        hosts: List[Dict] = None,
        migrate_type: str = "",
        redis_passwd: str = "",
    ) -> str:
        """
        启动迁移初始化任务（异步）
        对应原始 API: /migrateinit
        """
        job_id = X2cuService._create_migrate_job("init", host, migrate_type, hosts)

        from backend.tasks.osmigrate import migrate_init_task
        migrate_init_task.delay(job_id, host, port, username, password, hosts, migrate_type, redis_passwd)
        return job_id

    @staticmethod
    def start_migrate(
        job_name: str,
        host: str,
        port: str,
        username: str,
        password: str,
        hosts: List[Dict] = None,
        migrate_type: str = "",
    ) -> str:
        """
        启动迁移执行任务（异步）
        对应原始 API: /migrate
        """
        job_id = job_name or TaskService.generate_job_id("migrate")

        # 如果 job 不存在则创建
        if not MigrateJob.objects.filter(job_id=job_id).exists():
            MigrateJob.objects.create(
                job_id=job_id,
                job_type="migrate",
                target_host=host,
                migrate_type=migrate_type,
                hosts_json=hosts or [],
                status="running",
                progress=0,
            )
        else:
            X2cuService._update_migrate_job(job_id, status="running", progress=0)

        from backend.tasks.osmigrate import migrate_task
        migrate_task.delay(job_id, host, port, username, password, hosts, migrate_type)
        return job_id

    @staticmethod
    def start_migrate_back(
        job_name: str,
        host: str,
        port: str,
        username: str,
        password: str,
    ) -> str:
        """
        启动迁移回滚任务（异步）
        对应原始 API: /migrateback
        """
        job_id = job_name or TaskService.generate_job_id("migrate-back")

        if not MigrateJob.objects.filter(job_id=job_id).exists():
            MigrateJob.objects.create(
                job_id=job_id,
                job_type="migrate_back",
                target_host=host,
                status="running",
                progress=0,
            )
        else:
            X2cuService._update_migrate_job(job_id, status="running", progress=0)

        from backend.tasks.osmigrate import migrate_back_task
        migrate_back_task.delay(job_id, host, port, username, password)
        return job_id

    @staticmethod
    def get_migrate_status(job_id: str) -> Optional[dict]:
        """获取迁移任务状态"""
        try:
            job = MigrateJob.objects.get(job_id=job_id)
            return {
                "job_id": job.job_id,
                "job_type": job.job_type,
                "migrate_type": job.migrate_type,
                "target_host": job.target_host,
                "status": job.status,
                "progress": job.progress,
                "result": job.result,
                "error_message": job.error_message,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
            }
        except MigrateJob.DoesNotExist:
            return None
