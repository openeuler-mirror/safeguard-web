"""集群相关服务"""
import random
import string
import hashlib
import logging
from typing import Optional, Dict, List
from backend.models.host import Cluster, Host, VM
from backend.utils.hardware_collector import (
    collect_host_hardware,
    collect_host_lldp,
    update_host_hardware_info,
    update_host_lldp_info,
    collect_all_hardware_info,
)

logger = logging.getLogger(__name__)

# libvirt 状态映射
LIBVIRT_STATE_MAP = {
    0: 'nostate',      # VIR_DOMAIN_NOSTATE
    1: 'running',      # VIR_DOMAIN_RUNNING
    2: 'blocked',      # VIR_DOMAIN_BLOCKED
    3: 'paused',        # VIR_DOMAIN_PAUSED
    4: 'shutdown',      # VIR_DOMAIN_SHUTDOWN
    5: 'shutoff',       # VIR_DOMAIN_SHUTOFF
    6: 'crashed',       # VIR_DOMAIN_CRASHED
    7: 'suspended',     # VIR_DOMAIN_PMSUSPENDED
}


class ClusterService:
    """集群服务"""

    @staticmethod
    def list_clusters(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取集群列表（支持分页和过滤）"""
        queryset = Cluster.objects.all()
        if filters:
            queryset = queryset.filter(**filters)

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
    def get_cluster(cluster_id: int) -> Optional[Cluster]:
        """获取集群详情"""
        try:
            return Cluster.objects.get(pk=cluster_id)
        except Cluster.DoesNotExist:
            return None

    @staticmethod
    def create_cluster(data: dict) -> Cluster:
        """创建集群"""
        return Cluster.objects.create(**data)

    @staticmethod
    def update_cluster(cluster_id: int, data: dict) -> Optional[Cluster]:
        """更新集群"""
        try:
            cluster = Cluster.objects.get(pk=cluster_id)
            for key, value in data.items():
                setattr(cluster, key, value)
            cluster.save()
            return cluster
        except Cluster.DoesNotExist:
            return None

    @staticmethod
    def delete_cluster(cluster_id: int) -> bool:
        """删除集群"""
        try:
            cluster = Cluster.objects.get(pk=cluster_id)
            cluster.delete()
            return True
        except Cluster.DoesNotExist:
            return False

    @staticmethod
    def get_cluster_topology(cluster_id: int) -> Optional[Dict]:
        """
        获取集群拓扑

        返回集群下所有主机和VM的关联关系

        Returns:
            {
                'cluster': {...},
                'hosts': [...],
                'vms': [...],
                'lldp_topology': {...}  # 如果有LLDP信息
            }
        """
        try:
            cluster = Cluster.objects.get(pk=cluster_id)
        except Cluster.DoesNotExist:
            return None

        hosts = list(cluster.host_set.all())
        vms = list(VM.objects.filter(host__in=hosts).select_related('host', 'cluster'))

        # 构建 LLDP 拓扑信息
        lldp_topology = {}
        for host in hosts:
            if host.lldp_infos:
                lldp_topology[host.ip_address] = host.lldp_infos

        return {
            'cluster': {
                'id': cluster.id,
                'name': cluster.name,
                'description': cluster.description,
            },
            'hosts': [
                {
                    'id': h.id,
                    'hostname': h.hostname,
                    'ip_address': h.ip_address,
                    'status': h.status,
                    'lldp_count': len(h.lldp_infos) if h.lldp_infos else 0,
                }
                for h in hosts
            ],
            'vms': [
                {
                    'id': v.id,
                    'name': v.name,
                    'uuid': v.uuid,
                    'status': v.status,
                    'host_id': v.host_id,
                    'ip_address': v.ip_address,
                }
                for v in vms
            ],
            'lldp_topology': lldp_topology,
        }


class HostService:
    """主机服务"""

    @staticmethod
    def list_hosts(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取主机列表（支持分页和过滤）"""
        queryset = Host.objects.select_related('cluster').all()
        if filters:
            queryset = queryset.filter(**filters)

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
    def get_host(host_id: int) -> Optional[Host]:
        """获取主机详情"""
        try:
            return Host.objects.select_related('cluster').get(pk=host_id)
        except Host.DoesNotExist:
            return None

    @staticmethod
    def create_host(data: dict) -> Host:
        """创建主机"""
        return Host.objects.create(**data)

    @staticmethod
    def update_host(host_id: int, data: dict) -> Optional[Host]:
        """更新主机"""
        try:
            host = Host.objects.get(pk=host_id)
            for key, value in data.items():
                setattr(host, key, value)
            host.save()
            return host
        except Host.DoesNotExist:
            return None

    @staticmethod
    def delete_host(host_id: int) -> bool:
        """删除主机"""
        try:
            host = Host.objects.get(pk=host_id)
            host.delete()
            return True
        except Host.DoesNotExist:
            return False

    @staticmethod
    def collect_hardware(host_id: int) -> Dict:
        """
        采集主机硬件信息

        Args:
            host_id: 主机ID

        Returns:
            {
                'success': bool,
                'message': str,
                'data': {...}  # 硬件信息
            }
        """
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {'success': False, 'message': '主机不存在', 'data': None}

        success = update_host_hardware_info(host)
        if success:
            # 重新获取更新后的数据
            host.refresh_from_db()
            return {
                'success': True,
                'message': '硬件信息采集成功',
                'data': {
                    'arch_info': host.arch_info,
                    'uptime': host.uptime,
                    'os_version': host.os_version,
                    'cpu_info': host.cpu_info,
                    'disk_info': host.disk_info,
                    'memory_info': host.memory_info,
                    'network_info': host.network_info,
                }
            }
        else:
            return {'success': False, 'message': '硬件信息采集失败', 'data': None}

    @staticmethod
    def collect_lldp(host_id: int) -> Dict:
        """
        采集 LLDP 拓扑信息

        Args:
            host_id: 主机ID

        Returns:
            {
                'success': bool,
                'message': str,
                'data': [...]  # LLDP 信息列表
            }
        """
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {'success': False, 'message': '主机不存在', 'data': None}

        success = update_host_lldp_info(host)
        if success:
            host.refresh_from_db()
            return {
                'success': True,
                'message': 'LLDP 信息采集成功',
                'data': host.lldp_infos
            }
        else:
            return {'success': False, 'message': 'LLDP 信息采集失败', 'data': None}

    @staticmethod
    def get_host_lldp(host_id: int) -> Dict:
        """
        获取主机已保存的 LLDP 信息

        Args:
            host_id: 主机ID

        Returns:
            {
                'success': bool,
                'message': str,
                'data': [...]  # LLDP 信息列表
            }
        """
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {'success': False, 'message': '主机不存在', 'data': None}

        return {
            'success': True,
            'message': 'LLDP 信息获取成功',
            'data': host.lldp_infos or []
        }

    @staticmethod
    def collect_all(host_id: int) -> Dict:
        """
        采集主机所有硬件信息（包括 LLDP）

        Args:
            host_id: 主机ID

        Returns:
            {
                'success': bool,
                'message': str,
                'data': {
                    'hardware': {...},
                    'lldp': [...]
                }
            }
        """
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {'success': False, 'message': '主机不存在', 'data': None}

        try:
            # 采集硬件信息
            update_host_hardware_info(host)
            # 采集 LLDP 信息
            update_host_lldp_info(host)

            host.refresh_from_db()
            return {
                'success': True,
                'message': '信息采集成功',
                'data': {
                    'hardware': {
                        'arch_info': host.arch_info,
                        'uptime': host.uptime,
                        'os_version': host.os_version,
                        'cpu_info': host.cpu_info,
                        'disk_info': host.disk_info,
                        'memory_info': host.memory_info,
                        'network_info': host.network_info,
                        'mount_info': host.mount_info,
                        'dmesg_info': host.dmesg_info,
                    },
                    'lldp': host.lldp_infos
                }
            }
        except Exception as e:
            logger.error(f"Failed to collect all info for host {host_id}: {e}")
            return {'success': False, 'message': str(e), 'data': None}

    @staticmethod
    def generate_random_password(length: int = 16) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度

        Returns:
            随机密码字符串
        """
        charset = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(random.choice(charset) for _ in range(length))

    @staticmethod
    def hash_password(password: str, key: str = "culinux") -> str:
        """
        哈希密码

        Args:
            password: 明文密码
            key: 加密密钥

        Returns:
            哈希后的密码
        """
        hasher = hashlib.md5()
        hasher.update((password + key).encode('utf-8'))
        return hasher.hexdigest()

    @staticmethod
    def update_host_password(host_id: int, new_password: str = None, key: str = "culinux") -> Dict:
        """
        修改主机密码

        Args:
            host_id: 主机ID
            new_password: 新密码（如果为空则生成随机密码）
            key: 加密密钥

        Returns:
            {
                'success': bool,
                'message': str,
                'password': str  # 新密码
            }
        """
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {'success': False, 'message': '主机不存在', 'password': None}

        # 如果没有指定新密码，生成随机密码
        if not new_password:
            new_password = HostService.generate_random_password()

        # 加密密码
        encrypted_password = HostService.hash_password(new_password, key)

        # 更新数据库中的密码
        host.password = encrypted_password
        host.save()

        return {
            'success': True,
            'message': '密码更新成功',
            'password': new_password  # 返回明文密码
        }

    @staticmethod
    def import_hosts_from_excel(file_obj):
        """从 Excel 导入主机"""
        import openpyxl
        from io import BytesIO
        try:
            wb = openpyxl.load_workbook(BytesIO(file_obj.read()))
            ws = wb.active
            headers = [cell.value for cell in ws[1]]
            created_count = 0
            updated_count = 0
            errors = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                try:
                    data = dict(zip(headers, row))
                    if not data.get("hostname") or not data.get("ip_address"):
                        continue
                    host, created = Host.objects.update_or_create(
                        ip_address=data["ip_address"],
                        defaults={
                            "hostname": data.get("hostname", ""),
                            "port": data.get("port", 22),
                            "username": data.get("username", ""),
                            "password": data.get("password", ""),
                            "status": data.get("status", "offline"),
                            "os_type": data.get("os_type", ""),
                            "host_type": data.get("host_type", "VMHost"),
                            "cluster_id": data.get("cluster_id") or None,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(str(e))
            return {
                "success": True,
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "message": f"导入完成：新建 {created_count} 条，更新 {updated_count} 条，错误 {len(errors)} 条",
            }
        except Exception as e:
            logger.error(f"Import hosts from excel failed: {e}")
            return {"success": False, "message": str(e), "created": 0, "updated": 0, "errors": [str(e)]}

    @staticmethod
    def import_key_cloud(file_obj):
        """从骨干云部署表 Excel 导入主机

        支持的中文字段映射：
        序列号、IP地址、主机名、ntp地址、密码、设备分类、
        是否有集群属性、是否有专区属性、是否绑定cell、
        带外vlan、带内管理vlan、带内管理接口名称、
        存储vlan、存储网络接口名称、
        业务网络vlan、业务网络接口名称、
        其他网络vlan、其他网络接口名称、
        RAID要求、BIOS配置要求、
        双引擎系统盘分区要求(单位为M)、单引擎系统盘分区要求(单位为M)、
        双引擎推荐操作系统版本、单引擎操作系统、
        存储IP、业务IP、其他IP
        """
        import openpyxl
        from io import BytesIO
        try:
            wb = openpyxl.load_workbook(BytesIO(file_obj.read()))
            ws = wb.active
            column_names = [cell.value for cell in ws[1]]

            field_mappings = {
                "序列号": "serial_number",
                "IP地址": "ip_address",
                "主机名": "hostname",
                "ntp地址": "ntp_address",
                "密码": "password",
                "设备分类": "host_type",
                "是否有集群属性": "is_cluster_type",
                "是否有专区属性": "is_zone_type",
                "是否绑定cell": "is_bind_cell_type",
                "带外vlan": "ipmi_vlan",
                "带内管理vlan": "manage_vlan",
                "带内管理接口名称": "manage_nic1",
                "存储vlan": "storage_vlan",
                "存储网络接口名称": "storage_ifname",
                "业务网络vlan": "business_vlan",
                "业务网络接口名称": "business_ifname",
                "其他网络vlan": "other_vlan",
                "其他网络接口名称": "other_ifname",
                "RAID要求": "raid",
                "BIOS配置要求": "bios_config",
                "双引擎系统盘分区要求(单位为M)": "mount_info",
                "单引擎系统盘分区要求(单位为M)": "mount_info",
                "双引擎推荐操作系统版本": "os_version",
                "单引擎操作系统": "os_version",
                "存储IP": "storage_address",
                "业务IP": "business_address",
                "其他IP": "other_address",
            }
            flag_map = {"是": True, "否": False}

            created_count = 0
            updated_count = 0
            errors = []

            for row in ws.iter_rows(min_row=2, values_only=True):
                try:
                    row_data = dict(zip(column_names, row))
                    host_data = {}
                    for col_name, field_name in field_mappings.items():
                        if col_name in row_data and row_data[col_name] is not None:
                            value = str(row_data[col_name]).strip()
                            if field_name in ("is_cluster_type", "is_zone_type", "is_bind_cell_type"):
                                host_data[field_name] = flag_map.get(value, False)
                            else:
                                host_data[field_name] = value

                    if not host_data.get("hostname") or not host_data.get("ip_address"):
                        continue

                    if not host_data.get("username"):
                        host_data["username"] = "root"

                    # 原始逻辑：同名主机先删除再创建
                    existing = Host.objects.filter(hostname=host_data["hostname"]).first()
                    if existing:
                        existing.delete()
                        updated_count += 1
                    else:
                        created_count += 1

                    Host.objects.create(**host_data)
                except Exception as e:
                    errors.append(str(e))

            return {
                "success": True,
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "message": f"导入完成：新建 {created_count} 条，覆盖 {updated_count} 条，错误 {len(errors)} 条",
            }
        except Exception as e:
            logger.error(f"Import key cloud failed: {e}")
            return {"success": False, "message": str(e), "created": 0, "updated": 0, "errors": [str(e)]}

    @staticmethod
    def export_hosts_to_excel(filters=None):
        """导出主机到 Excel"""
        import openpyxl
        from io import BytesIO
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hosts"
        headers = [
            "hostname", "ip_address", "port", "username", "status",
            "os_type", "host_type", "cluster_name", "serial_number",
            "use_name", "use_for", "manage_nic1", "manage_nic2",
        ]
        ws.append(headers)
        queryset = Host.objects.select_related("cluster").all()
        if filters:
            queryset = queryset.filter(**filters)
        for host in queryset:
            ws.append([
                host.hostname,
                host.ip_address,
                host.port,
                host.username,
                host.status,
                host.os_type,
                host.host_type,
                host.cluster.name if host.cluster else "",
                host.serial_number or "",
                host.use_name or "",
                host.use_for or "",
                host.manage_nic1 or "",
                host.manage_nic2 or "",
            ])
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def remote_command(host_id, command):
        """在远程主机上执行命令"""
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {"success": False, "message": "主机不存在"}
        from backend.utils.ssh import SSHClient
        with SSHClient(host.ip_address, host.port, host.username, host.password, timeout=60) as client:
            stdout, stderr, exit_code = client.execute_command(command)
            return {
                "success": exit_code == 0,
                "message": "命令执行成功" if exit_code == 0 else stderr,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
            }

    @staticmethod
    def batch_update_password(host_ids, new_password=None, key="culinux"):
        """批量修改主机密码"""
        if not new_password:
            new_password = HostService.generate_random_password()
        encrypted_password = HostService.hash_password(new_password, key)
        updated = 0
        failed = []
        for host_id in host_ids:
            try:
                host = Host.objects.get(pk=host_id)
                host.password = encrypted_password
                host.save()
                updated += 1
            except Host.DoesNotExist:
                failed.append(f"Host {host_id} not found")
            except Exception as e:
                failed.append(f"Host {host_id}: {str(e)}")
        return {
            "success": len(failed) == 0,
            "message": f"更新完成：成功 {updated} 条，失败 {len(failed)} 条",
            "password": new_password,
            "updated": updated,
            "failed": failed,
        }


class VMService:
    """虚拟机服务"""

    @staticmethod
    def list_vms(filters: Optional[dict] = None, page: int = 1, page_size: int = 10):
        """获取VM列表（支持分页和过滤）"""
        queryset = VM.objects.select_related('host', 'cluster').all()
        if filters:
            queryset = queryset.filter(**filters)

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
    def get_vm(vm_id: int) -> Optional[VM]:
        """获取VM详情"""
        try:
            return VM.objects.select_related('host', 'cluster').get(pk=vm_id)
        except VM.DoesNotExist:
            return None

    @staticmethod
    def create_vm(data: dict) -> VM:
        """创建VM"""
        return VM.objects.create(**data)

    @staticmethod
    def update_vm(vm_id: int, data: dict) -> Optional[VM]:
        """更新VM"""
        try:
            vm = VM.objects.get(pk=vm_id)
            for key, value in data.items():
                setattr(vm, key, value)
            vm.save()
            return vm
        except VM.DoesNotExist:
            return None

    @staticmethod
    def delete_vm(vm_id: int) -> bool:
        """删除VM"""
        try:
            vm = VM.objects.get(pk=vm_id)
            vm.delete()
            return True
        except VM.DoesNotExist:
            return False

    @staticmethod
    def start_vm(vm_id: int) -> Dict:
        """
        启动 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                # libvirt 不可用，回退到模拟模式
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM启动成功（模拟模式）'}
            success, message = client.start_domain(vm.name)
            client.close()

            if success:
                vm.status = 'running'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            # libvirt 未安装，回退到模拟模式
            vm.status = 'running'
            vm.save()
            return {'success': True, 'message': 'VM启动成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to start VM {vm_id}: {e}")
            # 连接失败时回退到模拟模式
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM启动成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

    @staticmethod
    def stop_vm(vm_id: int) -> Dict:
        """
        停止 VM（强制关机）

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                vm.status = 'stopped'
                vm.save()
                return {'success': True, 'message': 'VM停止成功（模拟模式）'}
            success, message = client.stop_domain(vm.name)
            client.close()

            if success:
                vm.status = 'stopped'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            vm.status = 'stopped'
            vm.save()
            return {'success': True, 'message': 'VM停止成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to stop VM {vm_id}: {e}")
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.status = 'stopped'
                vm.save()
                return {'success': True, 'message': 'VM停止成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

    @staticmethod
    def reboot_vm(vm_id: int) -> Dict:
        """
        重启 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM重启成功（模拟模式）'}
            success, message = client.reboot_domain(vm.name)
            client.close()

            if success:
                vm.status = 'running'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            vm.status = 'running'
            vm.save()
            return {'success': True, 'message': 'VM重启成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to reboot VM {vm_id}: {e}")
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM重启成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

    @staticmethod
    def pause_vm(vm_id: int) -> Dict:
        """
        暂停 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                vm.status = 'paused'
                vm.save()
                return {'success': True, 'message': 'VM暂停成功（模拟模式）'}
            success, message = client.pause_domain(vm.name)
            client.close()

            if success:
                vm.status = 'paused'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            vm.status = 'paused'
            vm.save()
            return {'success': True, 'message': 'VM暂停成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to pause VM {vm_id}: {e}")
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.status = 'paused'
                vm.save()
                return {'success': True, 'message': 'VM暂停成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

    @staticmethod
    def resume_vm(vm_id: int) -> Dict:
        """
        恢复 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM恢复成功（模拟模式）'}
            success, message = client.resume_domain(vm.name)
            client.close()

            if success:
                vm.status = 'running'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            vm.status = 'running'
            vm.save()
            return {'success': True, 'message': 'VM恢复成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to resume VM {vm_id}: {e}")
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.status = 'running'
                vm.save()
                return {'success': True, 'message': 'VM恢复成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            success, message = client.resume_domain(vm.name)
            client.close()

            if success:
                vm.status = 'running'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            vm.status = 'running'
            vm.save()
            return {'success': True, 'message': 'VM恢复成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to resume VM {vm_id}: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_vm_status(vm_id: int) -> Dict:
        """
        获取 VM 状态

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str, 'status': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在', 'status': None}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            state = client.get_domain_state(vm.name)
            client.close()

            if state is not None:
                libvirt_status = LIBVIRT_STATE_MAP.get(state, 'unknown')
                return {'success': True, 'message': '查询成功', 'status': libvirt_status}
            else:
                return {'success': True, 'message': '查询成功（使用数据库状态）', 'status': vm.status}
        except ImportError:
            return {'success': True, 'message': '查询成功（使用数据库状态）', 'status': vm.status}
        except Exception as e:
            logger.error(f"Failed to get VM status {vm_id}: {e}")
            return {'success': True, 'message': '查询成功（使用数据库状态）', 'status': vm.status}

    @staticmethod
    def delete_vm_from_libvirt(vm_id: int) -> Dict:
        """
        从 libvirt 删除 VM（先关机再删除定义）

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                vm.delete()
                return {'success': True, 'message': 'VM删除成功（模拟模式）'}

            # 先尝试关机
            client.stop_domain(vm.name)
            # 再删除定义
            success, message = client.undefine_domain(vm.name)
            client.close()

            if success:
                # 从数据库删除
                vm.delete()
            return {'success': success, 'message': message}
        except ImportError:
            vm.delete()
            return {'success': True, 'message': 'VM删除成功（模拟模式）'}
        except Exception as e:
            logger.error(f"Failed to delete VM {vm_id}: {e}")
            if 'connection' in str(e).lower() or 'Failed to connect' in str(e):
                vm.delete()
                return {'success': True, 'message': 'VM删除成功（模拟模式）'}
            return {'success': False, 'message': str(e)}

    @staticmethod
    def create_vm_in_libvirt(vm_id: int) -> Dict:
        """
        在 libvirt 中创建 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        try:
            from backend.utils.libvirt_client import LibvirtClient

            host = vm.host
            client = LibvirtClient(
                host=host.ip_address,
                username=host.username,
                password=host.password,
            )
            conn = client._get_conn()
            if conn is None:
                return {'success': False, 'message': 'libvirt 连接失败，无法创建 VM'}

            # 生成 Domain XML
            xml = VMService._generate_domain_xml(vm)
            success, message = client.create_domain(xml)
            client.close()

            if success:
                vm.status = 'running'
                vm.save()
            return {'success': success, 'message': message}
        except ImportError:
            return {'success': False, 'message': 'libvirt 未安装'}
        except Exception as e:
            logger.error(f"Failed to create VM {vm_id}: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def _generate_domain_xml(vm: VM) -> str:
        """
        生成 libvirt Domain XML

        Args:
            vm: VM 实例

        Returns:
            XML 字符串
        """
        # 获取数据盘信息
        datadisks_xml = ""
        if vm.datadisk and isinstance(vm.datadisk, list):
            for i, disk in enumerate(vm.datadisk):
                disk_path = disk.get('path', '')
                if disk_path:
                    datadisks_xml += f'''
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='{disk_path}'/>
      <target dev='vd{"bcdefghijklmnopqrstuvwxyz"[i]}' bus='virtio'/>
    </disk>'''

        # 获取网桥信息
        netdevname = vm.vm_network_bridge or "mgmt"
        network_xml = f'''
    <interface type='bridge'>
      <source bridge='{netdevname}'/>
      <model type='virtio'/>
    </interface>'''

        # 内存单位转换（字节 -> GiB）
        memory_gib = max(vm.memory // (1024**3), 1)

        xml = f'''<domain type='kvm'>
  <name>{vm.name}</name>
  <memory unit='GiB'>{memory_gib}</memory>
  <currentMemory unit='GiB'>{memory_gib}</currentMemory>
  <vcpu placement='static'>{vm.vcpu}</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-2.9'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{vm.vm_image_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    {datadisks_xml}
    {network_xml}
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
  </devices>
</domain>'''
        return xml
    # ---------- Phase 3 新增：高级功能 ----------

    @staticmethod
    def import_hosts_from_excel(file_obj) -> dict:
        """从 Excel 导入主机"""
        import openpyxl
        from io import BytesIO
        try:
            wb = openpyxl.load_workbook(BytesIO(file_obj.read()))
            ws = wb.active
            headers = [cell.value for cell in ws[1]]
            created_count = 0
            updated_count = 0
            errors = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                try:
                    data = dict(zip(headers, row))
                    if not data.get("hostname") or not data.get("ip_address"):
                        continue
                    host, created = Host.objects.update_or_create(
                        ip_address=data["ip_address"],
                        defaults={
                            "hostname": data.get("hostname", ""),
                            "port": data.get("port", 22),
                            "username": data.get("username", ""),
                            "password": data.get("password", ""),
                            "status": data.get("status", "offline"),
                            "os_type": data.get("os_type", ""),
                            "host_type": data.get("host_type", "VMHost"),
                            "cluster_id": data.get("cluster_id") or None,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(str(e))
            return {
                "success": True,
                "created": created_count,
                "updated": updated_count,
                "errors": errors,
                "message": f"导入完成：新建 {created_count} 条，更新 {updated_count} 条，错误 {len(errors)} 条",
            }
        except Exception as e:
            logger.error(f"Import hosts from excel failed: {e}")
            return {"success": False, "message": str(e), "created": 0, "updated": 0, "errors": [str(e)]}

    @staticmethod
    def export_hosts_to_excel(filters: dict = None) -> bytes:
        """导出主机到 Excel"""
        import openpyxl
        from io import BytesIO
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hosts"
        headers = [
            "hostname", "ip_address", "port", "username", "status",
            "os_type", "host_type", "cluster_name", "serial_number",
            "use_name", "use_for", "manage_nic1", "manage_nic2",
        ]
        ws.append(headers)
        queryset = Host.objects.select_related("cluster").all()
        if filters:
            queryset = queryset.filter(**filters)
        for host in queryset:
            ws.append([
                host.hostname,
                host.ip_address,
                host.port,
                host.username,
                host.status,
                host.os_type,
                host.host_type,
                host.cluster.name if host.cluster else "",
                host.serial_number or "",
                host.use_name or "",
                host.use_for or "",
                host.manage_nic1 or "",
                host.manage_nic2 or "",
            ])
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def remote_command(host_id: int, command: str) -> dict:
        """在远程主机上执行命令"""
        try:
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return {"success": False, "message": "主机不存在"}
        from backend.utils.ssh import SSHClient
        with SSHClient(host.ip_address, host.port, host.username, host.password, timeout=60) as client:
            stdout, stderr, exit_code = client.execute_command(command)
            return {
                "success": exit_code == 0,
                "message": "命令执行成功" if exit_code == 0 else stderr,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
            }

    @staticmethod
    def batch_update_password(host_ids: List[int], new_password: str = None, key: str = "culinux") -> dict:
        """批量修改主机密码"""
        if not new_password:
            new_password = HostService.generate_random_password()
        encrypted_password = HostService.hash_password(new_password, key)
        updated = 0
        failed = []
        for host_id in host_ids:
            try:
                host = Host.objects.get(pk=host_id)
                host.password = encrypted_password
                host.save()
                updated += 1
            except Host.DoesNotExist:
                failed.append(f"Host {host_id} not found")
            except Exception as e:
                failed.append(f"Host {host_id}: {str(e)}")
        return {
            "success": len(failed) == 0,
            "message": f"更新完成：成功 {updated} 条，失败 {len(failed)} 条",
            "password": new_password,
            "updated": updated,
            "failed": failed,
        }
