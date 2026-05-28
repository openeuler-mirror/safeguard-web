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

        # TODO: 实现 libvirt 启动逻辑
        # 暂时只更新状态
        vm.status = 'running'
        vm.save()
        return {'success': True, 'message': 'VM启动功能待实现（libvirt集成）'}

    @staticmethod
    def stop_vm(vm_id: int) -> Dict:
        """
        停止 VM

        Args:
            vm_id: VM ID

        Returns:
            {'success': bool, 'message': str}
        """
        try:
            vm = VM.objects.get(pk=vm_id)
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在'}

        vm.status = 'stopped'
        vm.save()
        return {'success': True, 'message': 'VM停止功能待实现（libvirt集成）'}

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

        vm.status = 'running'
        vm.save()
        return {'success': True, 'message': 'VM重启功能待实现（libvirt集成）'}

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

        vm.status = 'paused'
        vm.save()
        return {'success': True, 'message': 'VM暂停功能待实现（libvirt集成）'}

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

        vm.status = 'running'
        vm.save()
        return {'success': True, 'message': 'VM恢复功能待实现（libvirt集成）'}

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
            return {'success': True, 'message': '查询成功', 'status': vm.status}
        except VM.DoesNotExist:
            return {'success': False, 'message': 'VM不存在', 'status': None}