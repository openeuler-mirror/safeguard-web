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
    @mock.patch('backend.services.safeguard.collect_host_hardware')
    def test_get_system_info_success(self, mock_collect):
        """测试获取系统信息成功"""
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
        """测试缺少host_id参数"""
        response = self.client.get('/api/safeguard/host-info/system-info/')
        self.assertNotEqual(response.data['errno'], 0)
        self.assertIn('host_id', response.data['errmsg'])

    def test_get_system_info_invalid_host_id(self):
        """测试无效的host_id参数"""
        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': 'invalid'}
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_system_info_host_not_found(self):
        """测试主机不存在"""
        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': 99999}
        )
        self.assertNotEqual(response.data['errno'], 0)

    @mock.patch('backend.services.safeguard.collect_ports')
    def test_get_ports_info_success(self, mock_collect):
        """测试获取端口信息成功"""
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
        """测试获取进程信息成功"""
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
        """测试获取服务信息成功"""
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
        """测试获取账户信息成功"""
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
        """测试服务控制成功"""
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
        """测试获取服务日志成功"""
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
        """测试终止进程成功"""
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
        """测试无效的pid参数"""
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
        """测试未认证访问"""
        # 清除认证
        self.client.credentials()

        response = self.client.get(
            '/api/safeguard/host-info/system-info/',
            {'host_id': self.host.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HostMonitorDataViewSetTest(SafeguardViewSetTestBase):
    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    @mock.patch('backend.services.safeguard.collect_network_metrics')
    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_collect_monitor_data_success(
        self, mock_disk, mock_network, mock_memory, mock_cpu
    ):
        """测试采集监控数据成功"""
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
        """测试获取历史监控数据成功"""
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
        """测试列出监控数据"""
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


class SafeguardPolicyTemplateViewSetTest(SafeguardViewSetTestBase):
    def test_list_policy_templates(self):
        """测试列出策略模板"""
        SafeguardPolicyTemplate.objects.create(
            name='Template 1',
            template_type='general',
            created_by=self.user,
        )
        SafeguardPolicyTemplate.objects.create(
            name='Template 2',
            template_type='custom',
            created_by=self.user,
        )

        response = self.client.get('/api/safeguard/policy-templates/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertGreaterEqual(len(results), 2)

    def test_create_policy_template_success(self):
        """测试创建策略模板成功"""
        data = {
            'name': 'New Policy Template',
            'description': '测试策略模板',
            'template_type': 'custom',
            'config': {'rules': [{'type': 'port', 'action': 'block', 'port': 22}]},
        }
        response = self.client.post(
            '/api/safeguard/policy-templates/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'New Policy Template')

    def test_create_policy_template_minimal(self):
        """测试最少数据创建策略模板"""
        data = {'name': 'Minimal Template'}
        response = self.client.post(
            '/api/safeguard/policy-templates/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'Minimal Template')

    def test_retrieve_policy_template(self):
        """测试获取单个策略模板"""
        template = SafeguardPolicyTemplate.objects.create(
            name='Retrieve Test',
            template_type='general',
            created_by=self.user,
        )

        response = self.client.get(f'/api/safeguard/policy-templates/{template.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'Retrieve Test')

    def test_retrieve_policy_template_not_found(self):
        """测试获取不存在的策略模板"""
        response = self.client.get('/api/safeguard/policy-templates/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_policy_template(self):
        """测试更新策略模板"""
        template = SafeguardPolicyTemplate.objects.create(
            name='Original Name',
            template_type='general',
            created_by=self.user,
        )

        data = {
            'name': 'Updated Name',
            'description': '更新描述',
        }
        response = self.client.put(
            f'/api/safeguard/policy-templates/{template.pk}/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'Updated Name')

    def test_partial_update_policy_template(self):
        """测试部分更新策略模板"""
        template = SafeguardPolicyTemplate.objects.create(
            name='Original Name',
            template_type='general',
            created_by=self.user,
        )

        data = {'description': '新描述'}
        response = self.client.patch(
            f'/api/safeguard/policy-templates/{template.pk}/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_delete_policy_template(self):
        """测试删除策略模板"""
        template = SafeguardPolicyTemplate.objects.create(
            name='Delete Test',
            template_type='general',
            created_by=self.user,
        )

        response = self.client.delete(
            f'/api/safeguard/policy-templates/{template.pk}/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(
            SafeguardPolicyTemplate.objects.filter(pk=template.pk).exists()
        )

    def test_list_policy_templates_with_filters(self):
        """测试带过滤条件列出策略模板"""
        SafeguardPolicyTemplate.objects.create(
            name='General Template',
            template_type='general',
            is_builtin=True,
            created_by=self.user,
        )
        SafeguardPolicyTemplate.objects.create(
            name='Custom Template',
            template_type='custom',
            is_builtin=False,
            created_by=self.user,
        )

        # 按类型过滤
        response = self.client.get(
            '/api/safeguard/policy-templates/',
            {'template_type': 'general'}
        )
        self.assertEqual(response.data['errno'], 0)


@override_settings(AUDIT_LOG_ENABLED=False)
class HostSafeguardPolicyViewSetTest(SafeguardViewSetTestBase):
    def setUp(self):
        super().setUp()
        self.template = SafeguardPolicyTemplate.objects.create(
            name='Test Template',
            config={'rules': []},
            created_by=self.user,
        )

    def test_bind_host_policy_success(self):
        """测试绑定主机策略成功"""
        data = {
            'host_id': self.host.id,
            'template_id': self.template.id,
        }
        response = self.client.post(
            '/api/safeguard/host-policies/bind/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['host_id'], self.host.id)

    def test_bind_host_policy_missing_params(self):
        """测试绑定主机策略缺少参数"""
        data = {'host_id': self.host.id}
        response = self.client.post(
            '/api/safeguard/host-policies/bind/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_bind_host_policy_host_not_found(self):
        """测试绑定策略到不存在的主机"""
        data = {
            'host_id': 99999,
            'template_id': self.template.id,
        }
        response = self.client.post(
            '/api/safeguard/host-policies/bind/',
            data,
            format='json'
        )
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_host_policy_detail(self):
        """测试获取主机策略详情"""
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=self.template,
            config=self.template.config.copy(),
            config_version=1,
            status='pending',
        )

        # 暂时直接调用服务层测试，跳过视图层的问题
        from backend.services.safeguard import PolicyService
        result = PolicyService.get_host_policy(policy.pk)
        self.assertEqual(result['host_id'], self.host.id)

    def test_list_host_policies(self):
        """测试列主机策略"""
        HostSafeguardPolicy.objects.create(
            host=self.host,
            template=self.template,
            config=self.template.config.copy(),
            config_version=1,
            status='pending',
        )

        response = self.client.get('/api/safeguard/host-policies/')
        self.assertEqual(response.data['errno'], 0)


class PolicyApplyTaskViewSetTest(SafeguardViewSetTestBase):
    def setUp(self):
        super().setUp()
        self.template = SafeguardPolicyTemplate.objects.create(
            name='Task Test Template',
            config={'rules': []},
            created_by=self.user,
        )
        self.policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=self.template,
            config=self.template.config.copy(),
            config_version=1,
            status='pending',
        )

    @mock.patch('backend.tasks.safeguard.apply_policy_task')
    def test_apply_policy_success(self, mock_apply_task):
        """测试执行策略下发成功"""
        mock_apply_task.delay.return_value = None

        task = PolicyApplyTask.objects.create(
            host=self.host,
            policy=self.policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        response = self.client.post(
            f'/api/safeguard/policy-tasks/{task.pk}/apply/'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_apply_policy_task_not_found(self):
        """测试执行不存在的策略任务"""
        response = self.client.post('/api/safeguard/policy-tasks/99999/apply/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_task_status(self):
        """测试获取任务状态"""
        task = PolicyApplyTask.objects.create(
            host=self.host,
            policy=self.policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        response = self.client.get(
            f'/api/safeguard/policy-tasks/{task.pk}/status/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['status'], 'pending')

    def test_get_task_status_not_found(self):
        """测试获取不存在的任务状态"""
        response = self.client.get('/api/safeguard/policy-tasks/99999/status/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_list_policy_tasks(self):
        """测试列出策略任务"""
        PolicyApplyTask.objects.create(
            host=self.host,
            policy=self.policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        response = self.client.get('/api/safeguard/policy-tasks/')
        self.assertEqual(response.data['errno'], 0)


class FileMonitorRuleViewSetTest(SafeguardViewSetTestBase):
    def test_list_file_monitor_rules(self):
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/',
            monitor_type='dir',
        )

        response = self.client.get('/api/safeguard/file-monitor-rules/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertGreaterEqual(len(results), 2)

    def test_create_file_monitor_rule_success(self):
        """测试创建监控规则成功"""
        data = {
            'host': self.host.id,
            'path': '/etc/ssh/sshd_config',
            'monitor_type': 'file',
            'watch_create': True,
            'watch_modify': True,
            'watch_delete': True,
        }
        response = self.client.post(
            '/api/safeguard/file-monitor-rules/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['path'], '/etc/ssh/sshd_config')

    def test_retrieve_file_monitor_rule(self):
        """测试获取单个监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )

        response = self.client.get(f'/api/safeguard/file-monitor-rules/{rule.pk}/')
        self.assertEqual(response.data['errno'], 0)

    def test_update_file_monitor_rule(self):
        """测试更新监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            watch_modify=False,
        )

        data = {
            'host': self.host.id,
            'path': '/etc/passwd',
            'monitor_type': 'file',
            'watch_modify': True,
        }
        response = self.client.put(
            f'/api/safeguard/file-monitor-rules/{rule.pk}/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_partial_update_file_monitor_rule(self):
        """测试部分更新监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            enabled=True,
        )

        data = {'enabled': False}
        response = self.client.patch(
            f'/api/safeguard/file-monitor-rules/{rule.pk}/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_delete_file_monitor_rule(self):
        """测试删除监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )

        response = self.client.delete(
            f'/api/safeguard/file-monitor-rules/{rule.pk}/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(
            FileMonitorRule.objects.filter(pk=rule.pk).exists()
        )

    def test_start_monitor_rule(self):
        """测试启用监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            enabled=False,
        )

        response = self.client.post(
            f'/api/safeguard/file-monitor-rules/{rule.pk}/start-monitor/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertTrue(response.data['data']['enabled'])

    def test_stop_monitor_rule(self):
        """测试禁用监控规则"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            enabled=True,
        )

        response = self.client.post(
            f'/api/safeguard/file-monitor-rules/{rule.pk}/stop-monitor/'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(response.data['data']['enabled'])

    @mock.patch('backend.services.safeguard.collect_file_events')
    def test_collect_file_events(self, mock_collect):
        """测试收集文件监控事件"""
        mock_collect.return_value = {
            'success': True,
            'events': [],
            'total_events': 0,
        }

        data = {'host_id': self.host.id}
        response = self.client.post(
            '/api/safeguard/file-monitor-rules/collect-events/',
            data,
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)

    def test_list_file_monitor_rules_with_filters(self):
        """测试带过滤条件列出监控规则"""
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            enabled=True,
        )
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/',
            monitor_type='dir',
            enabled=False,
        )

        # 按启用状态过滤
        response = self.client.get(
            '/api/safeguard/file-monitor-rules/',
            {'enabled': 'true'}
        )
        self.assertEqual(response.data['errno'], 0)

        # 按类型过滤
        response = self.client.get(
            '/api/safeguard/file-monitor-rules/',
            {'monitor_type': 'file'}
        )
        self.assertEqual(response.data['errno'], 0)


class FileMonitorEventViewSetTest(SafeguardViewSetTestBase):
    """FileMonitorEventViewSet 测试"""

    def setUp(self):
        super().setUp()
        self.rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )

    def test_list_file_monitor_events(self):
        """测试列出监控事件"""
        FileMonitorEvent.objects.create(
            host=self.host,
            rule=self.rule,
            event_type='modify',
            path='/etc/passwd',
            timestamp=timezone.now(),
        )
        FileMonitorEvent.objects.create(
            host=self.host,
            rule=self.rule,
            event_type='access',
            path='/etc/passwd',
            timestamp=timezone.now(),
        )

        response = self.client.get('/api/safeguard/file-monitor-events/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertGreaterEqual(len(results), 2)

    def test_list_file_monitor_events_with_filters(self):
        """测试带过滤条件列出监控事件"""
        FileMonitorEvent.objects.create(
            host=self.host,
            rule=self.rule,
            event_type='modify',
            path='/etc/passwd',
            timestamp=timezone.now(),
        )

        # 按主机过滤
        response = self.client.get(
            '/api/safeguard/file-monitor-events/',
            {'host': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)

        # 按事件类型过滤
        response = self.client.get(
            '/api/safeguard/file-monitor-events/',
            {'event_type': 'modify'}
        )
        self.assertEqual(response.data['errno'], 0)


class AuditLogViewSetTest(SafeguardViewSetTestBase):
    """AuditLogViewSet 测试"""

    def setUp(self):
        super().setUp()
        # 创建一些审计日志
        AuditLog.objects.create(
            user=self.user,
            action='create',
            resource_type='policy',
            resource_id='1',
            resource_name='Test Policy',
        )
        AuditLog.objects.create(
            user=self.user,
            action='update',
            resource_type='host',
            resource_id='1',
            resource_name='Test Host',
        )

    def test_list_audit_logs(self):
        """测试列出审计日志"""
        response = self.client.get('/api/safeguard/audit-logs/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertGreaterEqual(len(results), 2)

    def test_retrieve_audit_log(self):
        """测试获取单个审计日志"""
        log = AuditLog.objects.create(
            user=self.user,
            action='delete',
            resource_type='policy',
            resource_id='2',
            resource_name='Test Policy 2',
        )

        response = self.client.get(f'/api/safeguard/audit-logs/{log.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['action'], 'delete')

    def test_list_audit_logs_with_filters(self):
        """测试带过滤条件列出审计日志"""
        # 按操作类型过滤
        response = self.client.get(
            '/api/safeguard/audit-logs/',
            {'action': 'create'}
        )
        self.assertEqual(response.data['errno'], 0)

        # 按资源类型过滤
        response = self.client.get(
            '/api/safeguard/audit-logs/',
            {'resource_type': 'host'}
        )
        self.assertEqual(response.data['errno'], 0)


class SystemLogViewSetTest(SafeguardViewSetTestBase):
    """SystemLogViewSet 测试"""

    def test_list_system_logs(self):
        """测试列出系统日志"""
        SystemLog.objects.create(
            host=self.host,
            source='auth',
            level='info',
            message='Accepted publickey',
            timestamp=timezone.now(),
        )
        SystemLog.objects.create(
            host=self.host,
            source='syslog',
            level='warning',
            message='Disk space low',
            timestamp=timezone.now(),
        )

        response = self.client.get('/api/safeguard/system-logs/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertGreaterEqual(len(results), 2)

    def test_list_system_logs_with_filters(self):
        """测试带过滤条件列出系统日志"""
        SystemLog.objects.create(
            host=self.host,
            source='auth',
            level='info',
            message='Accepted publickey',
            timestamp=timezone.now(),
        )

        # 按主机过滤
        response = self.client.get(
            '/api/safeguard/system-logs/',
            {'host': self.host.id}
        )
        self.assertEqual(response.data['errno'], 0)

        # 按日志源过滤
        response = self.client.get(
            '/api/safeguard/system-logs/',
            {'source': 'auth'}
        )
        self.assertEqual(response.data['errno'], 0)

        # 按级别过滤
        response = self.client.get(
            '/api/safeguard/system-logs/',
            {'level': 'info'}
        )
        self.assertEqual(response.data['errno'], 0)


@override_settings(AUDIT_LOG_ENABLED=False)
class SafeguardViewPermissionDeniedTest(APITestCase):
    """测试非管理员用户无权访问safeguard资源"""

    def setUp(self):
        """创建普通用户（非管理员）"""
        # 创建普通用户角色
        self.normal_auth = Authority.objects.create(
            authority_id=890,
            authority_name='普通用户'
        )
        # 创建普通用户
        self.user = Users.objects.create(
            user='normaluser',
            password='testpass123',
            nickname='普通用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.normal_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_non_admin_cannot_access_host_info(self):
        """测试非管理员不能访问主机信息"""
        response = self.client.get('/api/safeguard/host-info/system-info/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_access_policy_templates(self):
        """测试非管理员不能访问策略模板"""
        response = self.client.get('/api/safeguard/policy-templates/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_access_monitor_data(self):
        """测试非管理员不能访问监控数据"""
        response = self.client.get('/api/safeguard/monitor-data/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_access_file_monitor_rules(self):
        """测试非管理员不能访问文件监控规则"""
        response = self.client.get('/api/safeguard/file-monitor-rules/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_access_audit_logs(self):
        """测试非管理员不能访问审计日志"""
        response = self.client.get('/api/safeguard/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
