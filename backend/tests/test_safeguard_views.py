"""Safeguard 相关视图集测试"""
from unittest import mock
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.host import Host
from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)
from backend.models.safeguard.monitor import HostMonitorData
from backend.models.safeguard.file_monitor import FileMonitorRule, FileMonitorEvent
from backend.models.audit.audit_log import AuditLog
from backend.models.audit.system_log import SystemLog
from django.test import override_settings
from django.utils import timezone


class SafeguardViewSetTestBase(APITestCase):
    """Safeguard 视图测试基类"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        # 创建管理员角色
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        # 创建测试用户
        self.user = Users.objects.create(
            user='safeguard_admin',
            password='testpass123',
            nickname='Safeguard管理员'
        )
        # 绑定管理员角色
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # 创建测试主机
        self.host = Host.objects.create(
            hostname='test-safeguard-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )


class HostInfoViewSetTest(SafeguardViewSetTestBase):
    """HostInfoViewSet 测试（TC-API-001到TC-API-011）"""

    @mock.patch('backend.services.safeguard.collect_host_hardware')
    def test_get_system_info_success(self, mock_collect):
        """测试获取系统信息成功（TC-API-001）"""
        mock_collect.return_value = {
            'success': True,
            'hostname': 'test-host',
            'os': 'Linux',
            'kernel': '5.4.0',
            'cpu': {'cores': 4, 'model': 'Intel i7'},
            'memory': {'total': 16384, 'used': 4096},
        }

        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    def test_get_system_info_missing_host_id(self):
        """测试缺少host_id参数（TC-API-010）"""
        response = self.client.get('/api/safeguard/host-info/system-info/')
        self.assertNotEqual(response.data['errno'], 0)
        self.assertIn('host_id', response.data['errmsg'])

    def test_get_system_info_invalid_host_id(self):
        """测试无效的host_id参数（TC-API-010）"""
        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': 'invalid'}
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_system_info_host_not_found(self):
        """测试主机不存在（TC-API-010）"""
        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': 99999}
        )
        self.assertNotEqual(response.data['errno'], 0)

    @mock.patch('backend.services.safeguard.collect_ports')
    def test_get_ports_info_success(self, mock_collect):
        """测试获取端口信息成功（TC-API-002）"""
        mock_collect.return_value = {
            'success': True,
            'listening_ports': [
                {'port': 22, 'protocol': 'tcp', 'process': 'sshd'},
            ],
            'high_risk_ports': [],
        }

        response = self.client.get(
            '/api/safeguard/host-info/ports-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    @mock.patch('backend.services.safeguard.collect_processes')
    def test_get_processes_info_success(self, mock_collect):
        """测试获取进程信息成功（TC-API-003）"""
        mock_collect.return_value = {
            'success': True,
            'processes': [
                {'pid': 1, 'name': 'systemd', 'cpu': 0.1, 'memory': 2.0},
            ],
            'high_resource': [],
        }

        response = self.client.get(
            '/api/safeguard/host-info/processes-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    @mock.patch('backend.services.safeguard.collect_services')
    def test_get_services_info_success(self, mock_collect):
        """测试获取服务信息成功（TC-API-004）"""
        mock_collect.return_value = {
            'success': True,
            'services': [
                {'name': 'sshd', 'status': 'running', 'enabled': True},
            ],
        }

        response = self.client.get(
            '/api/safeguard/host-info/services-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    @mock.patch('backend.services.safeguard.collect_system_accounts')
    def test_get_accounts_info_success(self, mock_collect):
        """测试获取账户信息成功（TC-API-005）"""
        mock_collect.return_value = {
            'success': True,
            'accounts': [
                {'username': 'root', 'uid': 0, 'gid': 0, 'shell': '/bin/bash'},
            ],
        }

        response = self.client.get(
            '/api/safeguard/host-info/accounts-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    @mock.patch('backend.services.safeguard.control_service')
    def test_service_control_success(self, mock_control):
        """测试服务控制成功（TC-API-006）"""
        mock_control.return_value = {
            'success': True,
            'service': 'sshd',
            'action': 'start',
            'message': 'Service started',
        }

        data = {
            'host_id': self.host.id,
            'service_name': 'sshd',
            'action': 'start'
        }
        response = self.client.post(
            '/api/safeguard/host-info/service-control/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    def test_service_control_missing_params(self):
        """测试服务控制缺少参数"""
        data = {'host_id': self.host.id}
        response = self.client.post(
            '/api/safeguard/host-info/service-control/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_service_control_invalid_action(self):
        """测试无效的action参数"""
        data = {
            'host_id': self.host.id,
            'service_name': 'sshd',
            'action': 'invalid'
        }
        response = self.client.post(
            '/api/safeguard/host-info/service-control/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    @mock.patch('backend.services.safeguard.get_service_logs')
    def test_get_service_logs_success(self, mock_get_logs):
        """测试获取服务日志成功（TC-API-007）"""
        mock_get_logs.return_value = {
            'success': True,
            'service': 'sshd',
            'logs': [
                {'timestamp': '2024-07-06 10:00:00', 'message': 'Accepted publickey'},
            ],
        }

        response = self.client.get(
            '/api/safeguard/host-info/service-logs/',
            {'host_id': self.host.id, 'service_name': 'sshd'}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    @mock.patch('backend.services.safeguard.kill_process')
    def test_kill_process_success(self, mock_kill):
        """测试终止进程成功（TC-API-008）"""
        mock_kill.return_value = {
            'success': True,
            'pid': 1234,
            'force': False,
            'message': 'Process killed',
        }

        data = {'host_id': self.host.id, 'pid': 1234}
        response = self.client.post(
            '/api/safeguard/host-info/kill-process/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['success'])

    def test_kill_process_invalid_pid(self):
        """测试无效的pid参数（TC-API-011）"""
        data = {'host_id': self.host.id, 'pid': 'invalid'}
        response = self.client.post(
            '/api/safeguard/host-info/kill-process/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_kill_process_missing_params(self):
        """测试终止进程缺少参数"""
        data = {'host_id': self.host.id}
        response = self.client.post(
            '/api/safeguard/host-info/kill-process/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_host_info_unauthenticated(self):
        """测试未认证访问（TC-API-009）"""
        # 清除认证
        self.client.credentials()

        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HostMonitorDataViewSetTest(SafeguardViewSetTestBase):
    """HostMonitorDataViewSet 测试（TC-API-012到TC-API-014）"""

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    @mock.patch('backend.services.safeguard.collect_network_metrics')
    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_collect_monitor_data_success(
        self, mock_disk, mock_network, mock_memory, mock_cpu
    ):
        """测试采集监控数据成功（TC-API-014）"""
        mock_cpu.return_value = {
            'success': True,
            'cpu_usage': {'usage_percent': 45.5},
            'load_avg': {'load_1min': 0.8, 'load_5min': 0.6, 'load_15min': 0.5},
        }
        mock_memory.return_value = {
            'success': True,
            'memory': {'mem_total': 16384, 'mem_used': 4096, 'mem_percent': 25.0},
        }
        mock_network.return_value = {
            'success': True,
            'total_rx_bytes': 1024000,
            'total_tx_bytes': 512000,
        }
        mock_disk.return_value = {
            'success': True,
            'disks': [{'sectors_read': 1000, 'sectors_written': 2000}],
        }

        data = {'host_id': self.host.id}
        response = self.client.post(
            '/api/safeguard/monitor-data/collect/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_collect_monitor_data_missing_host_id(self):
        """测试采集监控数据缺少host_id"""
        response = self.client.post(
            '/api/safeguard/monitor-data/collect/',
            {},
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    @mock.patch('backend.services.safeguard.collect_network_metrics')
    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_batch_collect_monitor_data(
        self, mock_disk, mock_network, mock_memory, mock_cpu
    ):
        """测试批量采集监控数据"""
        mock_cpu.return_value = {
            'success': True,
            'cpu_usage': {'usage_percent': 45.5},
            'load_avg': {'load_1min': 0.8, 'load_5min': 0.6, 'load_15min': 0.5},
        }
        mock_memory.return_value = {
            'success': True,
            'memory': {'mem_total': 16384, 'mem_used': 4096, 'mem_percent': 25.0},
        }
        mock_network.return_value = {
            'success': True,
            'total_rx_bytes': 1024000,
            'total_tx_bytes': 512000,
        }
        mock_disk.return_value = {
            'success': True,
            'disks': [{'sectors_read': 1000, 'sectors_written': 2000}],
        }

        data = {'host_ids': [self.host.id]}
        response = self.client.post(
            '/api/safeguard/monitor-data/batch_collect/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('results', response.data['data'])

    def test_get_monitor_history_success(self):
        """测试获取历史监控数据成功（TC-API-013）"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            memory_total=16384,
            memory_used=4096,
        )
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=50.0,
            load_1m=1.2,
            memory_total=16384,
            memory_used=8192,
        )

        response = self.client.get(
            '/api/safeguard/monitor-data/history/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertGreaterEqual(response.data['data']['total'], 2)

    def test_get_monitor_history_missing_host_id(self):
        """测试获取历史监控数据缺少host_id"""
        response = self.client.get('/api/safeguard/monitor-data/history/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_monitor_history_with_filters(self):
        """测试获取历史监控数据带过滤条件"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            memory_total=16384,
            memory_used=4096,
        )

        response = self.client.get(
            '/api/safeguard/monitor-data/history/',
            {'host_id': self.host.id, 'metric_type': 'cpu', 'page': 1, 'page_size': 10}
        )
        self.assertEqual(response.data['errno'], 0)

    def test_get_latest_monitor_data(self):
        """测试获取最新监控数据"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            memory_total=16384,
            memory_used=4096,
        )

        response = self.client.get(
            f'/api/safeguard/monitor-data/{self.host.id}/latest/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertIsNotNone(response.data['data'])

    def test_get_latest_monitor_data_not_found(self):
        """测试获取不存在主机的最新监控数据"""
        response = self.client.get('/api/safeguard/monitor-data/99999/latest/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_list_monitor_data(self):
        """测试列出监控数据（TC-API-012）"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            memory_total=16384,
            memory_used=4096,
        )

        response = self.client.get('/api/safeguard/monitor-data/')
        self.assertEqual(response.data['errno'], 0)
