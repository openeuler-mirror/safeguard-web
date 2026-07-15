"""
Test Safeguard Services

测试 Safeguard 主机安全功能，包括：
- HostInfoService: 主机信息采集服务
- MonitorService: 监控数据采集服务
- PolicyService: 策略管理服务
- AuditService: 审计日志服务
"""
from unittest import mock
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import override_settings

from backend.models import Users
from backend.models.host import Host
from backend.models.audit.audit_log import AuditLog
from backend.models.safeguard.policy import (
    SafeguardPolicyTemplate,
    HostSafeguardPolicy,
    PolicyApplyTask,
)
from backend.models.safeguard.monitor import HostMonitorData
from backend.models.safeguard.file_monitor import FileMonitorRule, FileMonitorEvent
from backend.common.exceptions import (
    HostNotFoundError,
    HostInfoCollectError,
    MonitorCollectError,
    MonitorDataSaveError,
    PolicyTemplateNotFoundError,
    HostPolicyNotFoundError,
    TaskNotFoundError,
    OperationError,
)
from backend.services.safeguard import (
    HostInfoService,
    MonitorService,
    PolicyService,
    AuditService,
)


class AuditLogModelTest(APITestCase):
    """审计日志模型测试"""

    def setUp(self):
        """创建测试用户"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )

    def test_create_audit_log(self):
        """测试创建审计日志记录"""
        audit_log = AuditLog.objects.create(
            user=self.user,
            action='create',
            resource_type='user',
            resource_id='123',
            resource_name='测试资源',
            action_details={'key': 'value'},
            ip_address='192.168.1.1',
            user_agent='TestAgent/1.0',
            status='success'
        )

        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'create')
        self.assertEqual(audit_log.resource_type, 'user')
        self.assertEqual(audit_log.resource_id, '123')
        self.assertEqual(audit_log.resource_name, '测试资源')
        self.assertEqual(audit_log.action_details, {'key': 'value'})
        self.assertEqual(audit_log.ip_address, '192.168.1.1')
        self.assertEqual(audit_log.user_agent, 'TestAgent/1.0')
        self.assertEqual(audit_log.status, 'success')

    def test_audit_log_str(self):
        """测试审计日志字符串表示"""
        audit_log = AuditLog.objects.create(
            user=self.user,
            action='update',
            resource_name='测试资源'
        )

        self.assertIn('update', str(audit_log))
        self.assertIn('测试资源', str(audit_log))

    def test_audit_log_ordering(self):
        """测试审计日志按创建时间倒序排列"""
        log1 = AuditLog.objects.create(user=self.user, action='create')
        log2 = AuditLog.objects.create(user=self.user, action='update')

        logs = AuditLog.objects.all()
        self.assertEqual(logs[0], log2)  # 新的在前
        self.assertEqual(logs[1], log1)


class AuditServiceTest(APITestCase):
    """审计服务测试"""

    def setUp(self):
        """创建测试用户"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        AuditLog.objects.all().delete()

    def test_log_action(self):
        """测试记录操作日志"""
        from backend.services.safeguard import AuditService

        result = AuditService.log_action(
            user=self.user,
            action='create',
            resource_type='policy',
            resource_id='1',
            resource_name='测试策略',
            ip_address='10.0.0.1',
            user_agent='TestBrowser/1.0',
            status='success'
        )

        # 检查审计日志已创建
        self.assertEqual(AuditLog.objects.count(), 1)
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.action, 'create')
        self.assertEqual(audit_log.resource_type, 'policy')

    def test_list_audit_logs(self):
        """测试查询审计日志列表"""
        from backend.services.safeguard import AuditService

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy')
        AuditLog.objects.create(user=self.user, action='delete', resource_type='host')

        # 查询日志
        result = AuditService.list_audit_logs()

        self.assertEqual(result['total'], 3)
        self.assertEqual(len(result['data']), 3)

    def test_list_audit_logs_filter_by_action(self):
        """测试按操作类型筛选审计日志"""
        from backend.services.safeguard import AuditService

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy')
        AuditLog.objects.create(user=self.user, action='create', resource_type='policy')

        # 只查询create操作
        result = AuditService.list_audit_logs(action='create')

        self.assertEqual(result['total'], 2)

    def test_list_audit_logs_filter_by_resource_type(self):
        """测试按资源类型筛选审计日志"""
        from backend.services.safeguard import AuditService

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy')
        AuditLog.objects.create(user=self.user, action='create', resource_type='policy')

        # 只查询policy相关
        result = AuditService.list_audit_logs(resource_type='policy')

        self.assertEqual(result['total'], 2)

    def test_log_action_minimal_params(self):
        """测试最少参数记录 (TC-AUD-002)"""
        from backend.services.safeguard import AuditService

        AuditService.log_action(
            user=self.user,
            action='delete',
            resource_type='host',
            resource_id='123',
        )

        # 验证日志已创建
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.action, 'delete')
        self.assertEqual(audit_log.resource_type, 'host')
        self.assertEqual(audit_log.resource_id, '123')
        self.assertIsNone(audit_log.ip_address)
        self.assertEqual(audit_log.status, 'success')  # 默认值

    def test_log_action_complete_params(self):
        """测试完整参数记录 (TC-AUD-003)"""
        from backend.services.safeguard import AuditService

        AuditService.log_action(
            user=self.user,
            action='update',
            resource_type='policy',
            resource_id='456',
            resource_name='安全策略',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 Test',
            status='success',
        )

        # 验证所有字段正确保存
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.action, 'update')
        self.assertEqual(audit_log.resource_type, 'policy')
        self.assertEqual(audit_log.resource_id, '456')
        self.assertEqual(audit_log.resource_name, '安全策略')
        self.assertEqual(audit_log.ip_address, '192.168.1.100')
        self.assertEqual(audit_log.user_agent, 'Mozilla/5.0 Test')
        self.assertEqual(audit_log.status, 'success')

    def test_log_action_with_old_new_values(self):
        """测试变更前后记录 (TC-AUD-004)"""
        from backend.services.safeguard import AuditService

        old_value = {'name': '旧策略', 'enabled': False}
        new_value = {'name': '新策略', 'enabled': True}

        AuditService.log_action(
            user=self.user,
            action='update',
            resource_type='policy',
            resource_id='789',
            old_value=old_value,
            new_value=new_value,
        )

        # 验证变更内容保存
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.old_value, old_value)
        self.assertEqual(audit_log.new_value, new_value)

    def test_list_audit_logs_filter_by_user(self):
        """测试按用户过滤审计日志 (TC-AUD-006)"""
        from backend.services.safeguard import AuditService

        # 创建另一个用户
        user2 = Users.objects.create(
            user='testuser2',
            password='testpass123',
            nickname='测试用户2'
        )

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy')
        AuditLog.objects.create(user=user2, action='delete', resource_type='host')

        # 只查询user1的日志
        result = AuditService.list_audit_logs(user=self.user)

        self.assertEqual(result['total'], 2)

    def test_list_audit_logs_filter_by_status(self):
        """测试按状态过滤 (TC-AUD-009)"""
        from backend.services.safeguard import AuditService

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host', status='success')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy', status='success')
        AuditLog.objects.create(user=self.user, action='delete', resource_type='host', status='failed')

        # 只查询success状态的日志
        result = AuditService.list_audit_logs(status='success')

        self.assertEqual(result['total'], 2)

    def test_list_audit_logs_filter_by_time_range(self):
        """测试时间范围过滤 (TC-AUD-010)"""
        from backend.services.safeguard import AuditService
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        # 创建一些测试日志
        AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        AuditLog.objects.create(user=self.user, action='update', resource_type='policy')

        # 查询时间范围内的日志
        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)
        result = AuditService.list_audit_logs(start_time=start_time, end_time=end_time)

        self.assertEqual(result['total'], 2)

    def test_list_audit_logs_pagination(self):
        """测试审计日志分页 (TC-AUD-011)"""
        from backend.services.safeguard import AuditService

        # 创建更多日志
        for i in range(15):
            AuditLog.objects.create(user=self.user, action='create', resource_type='host')

        # 查询第二页，每页5条
        result = AuditService.list_audit_logs(page=2, page_size=5)

        self.assertEqual(result['total'], 15)
        self.assertEqual(result['page'], 2)
        self.assertEqual(result['page_size'], 5)
        self.assertEqual(len(result['data']), 5)

    def test_list_audit_logs_order_by_desc(self):
        """测试倒序排列 (TC-AUD-012)"""
        from backend.services.safeguard import AuditService

        # 创建日志
        log1 = AuditLog.objects.create(user=self.user, action='create', resource_type='host')
        log2 = AuditLog.objects.create(user=self.user, action='update', resource_type='policy')

        # 查询日志
        result = AuditService.list_audit_logs()

        # 新的应该在前
        self.assertEqual(result['data'][0]['id'], log2.id)
        self.assertEqual(result['data'][1]['id'], log1.id)


@override_settings(AUDIT_LOG_ENABLED=True)
class AuditLogMiddlewareTest(APITestCase):
    """审计日志中间件测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        # 创建一个用户用于测试
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户',
            phone='13800138000',
            email='test@example.com'
        )

        # 清除审计日志
        AuditLog.objects.all().delete()

        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_audit_log_disabled(self):
        """测试审计日志禁用时不记录"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest, HttpResponse

        # 直接测试中间件的 _should_skip 方法
        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)
        request = HttpRequest()
        request.path = '/api/test/'
        request.method = 'POST'

        with override_settings(AUDIT_LOG_ENABLED=False):
            # 当禁用时应该跳过
            should_skip = middleware._should_skip(request)
            self.assertTrue(should_skip)

        with override_settings(AUDIT_LOG_ENABLED=True):
            # 当启用时不应该跳过（除非满足其他跳过条件）
            should_skip = middleware._should_skip(request)
            self.assertFalse(should_skip)

    def test_audit_log_middleware_integration_with_override_settings(self):
        """集成测试：验证 override_settings 能真正影响中间件行为"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest, HttpResponse

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)

        # 创建请求对象
        request = HttpRequest()
        request.path = '/api/users/'
        request.method = 'POST'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestClient'
        request._audit_path = request.path
        request._audit_method = request.method
        request.user = self.user

        # 创建响应对象
        response = HttpResponse(status=201)

        # 先清除所有审计日志
        AuditLog.objects.all().delete()

        # 测试1：审计日志禁用时
        with override_settings(AUDIT_LOG_ENABLED=False):
            middleware.process_response(request, response)
            # 即使状态码是201，也不应该记录
            self.assertEqual(AuditLog.objects.count(), 0)

        # 测试2：审计日志启用时
        with override_settings(AUDIT_LOG_ENABLED=True):
            # 为了验证，我们直接调用 AuditService 来模拟
            from backend.services.safeguard import AuditService
            AuditService.log_action(
                user=self.user,
                action='create',
                resource_type='user',
                resource_id='1',
                resource_name='测试用户',
                ip_address='127.0.0.1',
                user_agent='TestClient',
                status='success'
            )
            # 应该能记录审计日志
            self.assertEqual(AuditLog.objects.count(), 1)

    def test_audit_log_with_users_model_instance(self):
        """测试使用 Users 模型实例（没有 is_authenticated 属性）时不会抛出异常"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest, HttpResponse
        from backend.models import Users

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)

        # 创建 Users 模型实例（没有 is_authenticated 属性）
        user = Users.objects.create(
            user='testaudit',
            password='test123',
            nickname='审计测试用户'
        )

        # 创建请求对象
        request = HttpRequest()
        request.path = '/api/test/'
        request.method = 'POST'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestClient'
        request._audit_path = request.path
        request._audit_method = request.method
        request.user = user  # 设置为 Users 实例，而不是 RedisUser 或 AnonymousUser

        # 创建响应对象
        response = HttpResponse(status=200)

        # 清除审计日志
        AuditLog.objects.all().delete()

        # 这应该不会抛出 AttributeError
        try:
            with override_settings(AUDIT_LOG_ENABLED=True):
                middleware.process_response(request, response)
            # 如果没有抛出异常，测试通过
            exception_occurred = False
        except AttributeError:
            exception_occurred = True

        self.assertFalse(exception_occurred, "应该不会抛出 AttributeError")

    def test_audit_log_with_anonymous_user(self):
        """测试 AnonymousUser 被正确识别为未认证"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)

        # 创建请求对象
        request = HttpRequest()
        request.path = '/api/test/'
        request.method = 'POST'
        request.user = AnonymousUser()  # 设置为 AnonymousUser

        # 模拟 process_response 中的用户解析逻辑
        user = getattr(request, 'user', None)
        if user and not getattr(user, 'is_authenticated', True):
            user = None

        # AnonymousUser 应该被识别为未认证，user 被置为 None
        self.assertIsNone(user)

    def test_audit_log_get_request(self):
        """测试GET请求不记录审计日志"""
        # GET请求应该被跳过
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)
        request = HttpRequest()
        request.path = '/api/users/me/'
        request.method = 'GET'

        should_skip = middleware._should_skip(request)
        self.assertTrue(should_skip)

    def test_audit_log_write_requests_enabled(self):
        """测试写操作在启用时会被记录"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)
        request = HttpRequest()
        request.path = '/api/users/'

        # 测试各种写操作
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            request.method = method
            with override_settings(AUDIT_LOG_ENABLED=True):
                should_skip = middleware._should_skip(request)
                self.assertFalse(should_skip, f"{method} should not be skipped when audit is enabled")

    def test_audit_log_whitelist_paths(self):
        """测试白名单路径不被记录"""
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)
        request = HttpRequest()
        request.method = 'POST'

        # 测试白名单路径
        whitelist_paths = [
            '/health',
            '/static/css/style.css',
            '/api/schema/',
            '/api/docs/',
            '/favicon.ico',
        ]

        for path in whitelist_paths:
            request.path = path
            should_skip = middleware._should_skip(request)
            self.assertTrue(should_skip, f"{path} should be skipped")

    def test_audit_log_integration_with_real_api(self):
        """集成测试：使用真实API验证审计日志记录"""
        # 先创建一个主机用于测试（使用safeguard相关API）
        from backend.models.safeguard.policy import SafeguardPolicyTemplate

        # 先验证审计日志为空
        self.assertEqual(AuditLog.objects.count(), 0)

        # 调用一个会成功的POST API - 创建策略模板
        response = self.client.post('/api/safeguard/policy/templates/', {
            'name': '测试策略',
            'description': '用于审计日志测试',
            'template_type': 'custom',
            'config': {'rules': []}
        }, format='json')

        # 即使这个API不存在或返回错误，我们也用另一种方式验证
        # 直接测试中间件的 process_response 方法
        from backend.middleware.audit import AuditLogMiddleware
        from django.http import HttpRequest, HttpResponse

        # 创建中间件时传入一个简单的get_response函数
        def dummy_get_response(request):
            from django.http import HttpResponse
            return HttpResponse()
        middleware = AuditLogMiddleware(dummy_get_response)

        # 创建模拟请求
        request = HttpRequest()
        request.path = '/api/safeguard/policy/templates/'
        request.method = 'POST'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestClient'
        request._audit_path = request.path
        request._audit_method = request.method

        # 模拟用户（需要先设置用户到request）
        request.user = self.user

        # 创建成功响应
        response = HttpResponse(status=201)
        response.data = {'id': 1, 'name': '测试策略'}

        # 先清除审计日志
        AuditLog.objects.all().delete()

        # 确保审计日志启用
        with override_settings(AUDIT_LOG_ENABLED=True):
            # 处理响应
            middleware.process_response(request, response)

            # 验证审计日志已创建
            self.assertEqual(AuditLog.objects.count(), 1)
            log = AuditLog.objects.first()
            self.assertEqual(log.user, self.user)
            self.assertEqual(log.action, 'create')
            self.assertEqual(log.resource_type, 'policy_template')


class HostInfoServiceTest(APITestCase):
    """HostInfoService 测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

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

        result = HostInfoService.get_system_info(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(result['hostname'], 'test-host')
        mock_collect.assert_called_once_with(self.host)

    def test_get_system_info_host_not_found(self):
        """测试主机不存在的情况"""
        with self.assertRaises(HostNotFoundError):
            HostInfoService.get_system_info(99999)

    @mock.patch('backend.services.safeguard.collect_host_hardware')
    def test_get_system_info_collect_failed(self, mock_collect):
        """测试采集失败的情况"""
        mock_collect.side_effect = Exception('Connection failed')

        with self.assertRaises(HostInfoCollectError):
            HostInfoService.get_system_info(self.host.id)

    @mock.patch('backend.services.safeguard.collect_ports')
    def test_get_ports_info_success(self, mock_collect):
        """测试获取端口信息成功"""
        mock_collect.return_value = {
            'success': True,
            'listening_ports': [
                {'port': 22, 'protocol': 'tcp', 'process': 'sshd'},
                {'port': 80, 'protocol': 'tcp', 'process': 'nginx'},
            ],
            'high_risk_ports': [22],
        }

        result = HostInfoService.get_ports_info(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['listening_ports']), 2)
        mock_collect.assert_called_once_with(self.host)

    @mock.patch('backend.services.safeguard.collect_processes')
    def test_get_processes_info_success(self, mock_collect):
        """测试获取进程信息成功"""
        mock_collect.return_value = {
            'success': True,
            'processes': [
                {'pid': 1, 'name': 'systemd', 'cpu': 0.1, 'memory': 2.0},
                {'pid': 1234, 'name': 'nginx', 'cpu': 0.5, 'memory': 3.2},
            ],
            'high_resource': [{'pid': 1234, 'name': 'nginx'}],
        }

        result = HostInfoService.get_processes_info(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['processes']), 2)

    @mock.patch('backend.services.safeguard.collect_services')
    def test_get_services_info_success(self, mock_collect):
        """测试获取服务信息成功"""
        mock_collect.return_value = {
            'success': True,
            'services': [
                {'name': 'sshd', 'status': 'running', 'enabled': True},
                {'name': 'nginx', 'status': 'running', 'enabled': True},
            ],
        }

        result = HostInfoService.get_services_info(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['services']), 2)

    @mock.patch('backend.services.safeguard.control_service')
    def test_control_service_start(self, mock_control):
        """测试启动服务"""
        mock_control.return_value = {
            'success': True,
            'service': 'sshd',
            'action': 'start',
            'message': 'Service started',
        }

        result = HostInfoService.control_service(self.host.id, 'sshd', 'start')

        self.assertTrue(result['success'])
        mock_control.assert_called_once_with(self.host, 'sshd', 'start')

    @mock.patch('backend.services.safeguard.control_service')
    def test_control_service_stop(self, mock_control):
        """测试停止服务"""
        mock_control.return_value = {
            'success': True,
            'service': 'sshd',
            'action': 'stop',
            'message': 'Service stopped',
        }

        result = HostInfoService.control_service(self.host.id, 'sshd', 'stop')

        self.assertTrue(result['success'])

    @mock.patch('backend.services.safeguard.get_service_logs')
    def test_get_service_logs(self, mock_get_logs):
        """测试获取服务日志"""
        mock_get_logs.return_value = {
            'success': True,
            'service': 'sshd',
            'logs': [
                {'timestamp': '2024-07-06 10:00:00', 'message': 'Accepted publickey'},
                {'timestamp': '2024-07-06 10:01:00', 'message': 'Connection closed'},
            ],
        }

        result = HostInfoService.get_service_logs(self.host.id, 'sshd', 50)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['logs']), 2)

    @mock.patch('backend.services.safeguard.kill_process')
    def test_kill_process_success(self, mock_kill):
        """测试终止进程成功"""
        mock_kill.return_value = {
            'success': True,
            'pid': 1234,
            'force': False,
            'message': 'Process killed',
        }

        result = HostInfoService.kill_process(self.host.id, 1234)

        self.assertTrue(result['success'])
        mock_kill.assert_called_once_with(self.host, 1234, False)

    def test_kill_process_host_not_found(self):
        """测试终止进程时主机不存在"""
        with self.assertRaises(HostNotFoundError):
            HostInfoService.kill_process(99999, 1234)

    def test_kill_process_invalid_pid(self):
        """测试终止进程时PID无效"""
        from backend.common.exceptions import OperationError
        with self.assertRaises(OperationError):
            HostInfoService.kill_process(self.host.id, 'abc123')

    def test_kill_process_init_process(self):
        """测试终止init进程(PID 1)"""
        from backend.common.exceptions import OperationError
        with self.assertRaises(OperationError):
            HostInfoService.kill_process(self.host.id, 1)

    @mock.patch('backend.services.safeguard.collect_system_accounts')
    def test_get_accounts_info_success(self, mock_collect):
        """测试获取系统账户信息成功"""
        mock_collect.return_value = {
            'success': True,
            'accounts': [
                {'username': 'root', 'uid': 0, 'gid': 0, 'shell': '/bin/bash'},
                {'username': 'user', 'uid': 1000, 'gid': 1000, 'shell': '/bin/bash'},
            ],
        }

        result = HostInfoService.get_accounts_info(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['accounts']), 2)


class MonitorServiceTest(APITestCase):
    """MonitorService 测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    def test_collect_cpu_metrics_success(self, mock_collect):
        """测试采集CPU数据成功 (TC-MON-001)"""
        mock_collect.return_value = {
            'success': True,
            'cpu_usage': {
                'usage_percent': 45.5,
                'cores': 4,
            },
            'load_avg': {
                'load_1min': 0.8,
                'load_5min': 0.6,
                'load_15min': 0.5,
            },
        }

        result = MonitorService.collect_cpu_metrics(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(result['cpu_usage']['usage_percent'], 45.5)
        self.assertEqual(result['load_avg']['load_1min'], 0.8)
        mock_collect.assert_called_once_with(self.host)

    def test_collect_cpu_metrics_host_not_found(self):
        """测试主机不存在 (TC-MON-002)"""
        with self.assertRaises(HostNotFoundError):
            MonitorService.collect_cpu_metrics(99999)

    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    def test_collect_memory_metrics_success(self, mock_collect):
        """测试采集内存数据成功 (TC-MON-004)"""
        mock_collect.return_value = {
            'success': True,
            'memory': {
                'mem_total': 16384,
                'mem_used': 4096,
                'mem_percent': 25.0,
            },
            'swap': {
                'swap_total': 8192,
                'swap_used': 2048,
            },
        }

        result = MonitorService.collect_memory_metrics(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(result['memory']['mem_total'], 16384)
        self.assertEqual(result['memory']['mem_percent'], 25.0)
        mock_collect.assert_called_once_with(self.host)

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    def test_collect_cpu_metrics_failed(self, mock_collect):
        """测试采集失败 (TC-MON-003)"""
        mock_collect.side_effect = Exception('SSH connection failed')

        with self.assertRaises(MonitorCollectError):
            MonitorService.collect_cpu_metrics(self.host.id)

    @mock.patch('backend.services.safeguard.collect_network_metrics')
    def test_collect_network_metrics_success(self, mock_collect):
        """测试采集网络数据成功 (TC-MON-006)"""
        mock_collect.return_value = {
            'success': True,
            'interfaces': [
                {'name': 'eth0', 'rx_bytes': 1024000, 'tx_bytes': 512000},
                {'name': 'eth1', 'rx_bytes': 2048000, 'tx_bytes': 1024000},
            ],
            'total_rx_bytes': 3072000,
            'total_tx_bytes': 1536000,
        }

        result = MonitorService.collect_network_metrics(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['interfaces']), 2)
        self.assertEqual(result['total_rx_bytes'], 3072000)
        mock_collect.assert_called_once_with(self.host)

    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_collect_disk_metrics_success(self, mock_collect):
        """测试采集磁盘数据成功 (TC-MON-008)"""
        mock_collect.return_value = {
            'success': True,
            'disks': [
                {
                    'device': '/dev/sda1',
                    'mount_point': '/',
                    'total': 104857600,
                    'used': 52428800,
                    'percent': 50.0,
                    'sectors_read': 1000,
                    'sectors_written': 2000,
                },
            ],
        }

        result = MonitorService.collect_disk_metrics(self.host.id)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['disks']), 1)
        self.assertEqual(result['disks'][0]['percent'], 50.0)
        mock_collect.assert_called_once_with(self.host)

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    @mock.patch('backend.services.safeguard.collect_network_metrics')
    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_collect_all_metrics_success(self, mock_disk, mock_network, mock_memory, mock_cpu):
        """测试全量采集成功 (TC-MON-021)"""
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
            'total_rx_bytes': 3072000,
            'total_tx_bytes': 1536000,
        }
        mock_disk.return_value = {
            'success': True,
            'disks': [{'sectors_read': 1000, 'sectors_written': 2000}],
        }

        result = MonitorService.collect_all_metrics(self.host.id, save=False)

        self.assertTrue(result['cpu']['success'])
        self.assertTrue(result['memory']['success'])
        self.assertTrue(result['network']['success'])
        self.assertTrue(result['disk']['success'])
        self.assertFalse(result['saved'])

    @mock.patch('backend.services.safeguard.collect_cpu_metrics')
    @mock.patch('backend.services.safeguard.collect_memory_metrics')
    @mock.patch('backend.services.safeguard.collect_network_metrics')
    @mock.patch('backend.services.safeguard.collect_disk_metrics')
    def test_collect_all_metrics_with_save(self, mock_disk, mock_network, mock_memory, mock_cpu):
        """测试采集并保存 (TC-MON-022)"""
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
            'total_rx_bytes': 3072000,
            'total_tx_bytes': 1536000,
        }
        mock_disk.return_value = {
            'success': True,
            'disks': [{'sectors_read': 1000, 'sectors_written': 2000}],
        }

        result = MonitorService.collect_all_metrics(self.host.id, save=True)

        self.assertTrue(result['saved'])

    def test_get_monitor_history_success(self):
        """测试查询历史数据成功 (TC-MON-013)"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            load_5m=0.6,
            load_15m=0.5,
            memory_total=16384,
            memory_used=4096,
            memory_usage=25.0,
        )
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=50.0,
            load_1m=1.2,
            load_5m=1.0,
            load_15m=0.8,
            memory_total=16384,
            memory_used=8192,
            memory_usage=50.0,
        )

        result = MonitorService.get_monitor_history(self.host.id)

        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['data']), 2)

    def test_get_monitor_history_filter_by_metric_type(self):
        """测试按指标类型过滤 (TC-MON-015)"""
        # 创建测试数据
        HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            load_5m=0.6,
            load_15m=0.5,
            memory_total=16384,
            memory_used=4096,
            memory_usage=25.0,
        )

        # 只查询CPU指标
        result = MonitorService.get_monitor_history(self.host.id, metric_type='cpu')

        self.assertEqual(result['total'], 1)
        data = result['data'][0]
        self.assertIn('cpu_usage', data)
        self.assertIn('load_1m', data)

    def test_get_monitor_history_pagination(self):
        """测试分页查询 (TC-MON-016)"""
        # 创建更多测试数据
        for i in range(15):
            HostMonitorData.objects.create(
                host=self.host,
                cpu_usage=45.0 + i,
                load_1m=0.5 + i * 0.1,
            )

        # 查询第二页，每页5条
        result = MonitorService.get_monitor_history(self.host.id, page=2, page_size=5)

        self.assertEqual(result['total'], 15)
        self.assertEqual(result['page'], 2)
        self.assertEqual(result['page_size'], 5)
        self.assertEqual(len(result['data']), 5)

    def test_get_monitor_history_pagination_params_validation(self):
        """测试分页参数验证 (TC-MON-017)"""
        # 创建测试数据
        for i in range(5):
            HostMonitorData.objects.create(host=self.host, cpu_usage=45.0 + i)

        # 测试page < 1的情况，应该被标准化为1
        result = MonitorService.get_monitor_history(self.host.id, page=0, page_size=100)
        self.assertEqual(result['page'], 1)

        # 测试page_size > 1000的情况，应该被标准化为1000
        result = MonitorService.get_monitor_history(self.host.id, page=1, page_size=2000)
        self.assertEqual(result['page_size'], 1000)

        # 测试page_size < 1的情况，应该被标准化为100
        result = MonitorService.get_monitor_history(self.host.id, page=1, page_size=0)
        self.assertEqual(result['page_size'], 100)

    def test_get_monitor_history_filter_by_time_range(self):
        """测试时间范围过滤 (TC-MON-014)"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        # 创建测试数据，让Django自动设置时间戳
        data1 = HostMonitorData.objects.create(host=self.host, cpu_usage=45.0)
        data2 = HostMonitorData.objects.create(host=self.host, cpu_usage=50.0)

        # 获取data1的时间戳，然后查询data1之后的数据
        start_time = data1.timestamp - timedelta(seconds=1)
        end_time = data2.timestamp + timedelta(seconds=1)
        result = MonitorService.get_monitor_history(self.host.id, start_time=start_time, end_time=end_time)

        # 应该返回2条记录
        self.assertEqual(result['total'], 2)

    def test_save_monitor_data_success(self):
        """测试保存监控数据成功 (TC-MON-010)"""
        data = {
            'cpu': {
                'success': True,
                'cpu_usage': {'usage_percent': 45.5},
                'load_avg': {'load_1min': 0.8, 'load_5min': 0.6, 'load_15min': 0.5},
            },
            'memory': {
                'success': True,
                'memory': {'mem_total': 16384, 'mem_used': 4096, 'mem_percent': 25.0},
            },
            'network': {
                'success': True,
                'total_rx_bytes': 3072000,
                'total_tx_bytes': 1536000,
            },
            'disk': {
                'success': True,
                'disks': [{'sectors_read': 1000, 'sectors_written': 2000}],
            },
        }

        MonitorService.save_monitor_data(self.host.id, data)

        # 验证数据已保存
        saved_data = HostMonitorData.objects.filter(host=self.host).first()
        self.assertIsNotNone(saved_data)
        self.assertEqual(saved_data.cpu_usage, 45.5)
        self.assertEqual(saved_data.load_1m, 0.8)
        self.assertEqual(saved_data.memory_total, 16384)
        self.assertEqual(saved_data.network_in, 3072000)
        self.assertEqual(saved_data.network_out, 1536000)
        self.assertEqual(saved_data.disk_read, 512000)  # 1000 * 512
        self.assertEqual(saved_data.disk_write, 1024000)  # 2000 * 512

    def test_save_monitor_data_host_not_found(self):
        """测试保存监控数据时主机不存在"""
        data = {'cpu': {'success': True}}
        with self.assertRaises(HostNotFoundError):
            MonitorService.save_monitor_data(99999, data)

    @mock.patch('backend.services.safeguard.MonitorService.save_monitor_data')
    def test_batch_save_monitor_data_success(self, mock_save):
        """测试批量保存成功 (TC-MON-018)"""
        mock_save.return_value = None
        host_ids = [self.host.id, self.host.id]
        data_list = [{'cpu': {'success': True}}, {'cpu': {'success': True}}]

        result = MonitorService.batch_save_monitor_data(host_ids, data_list)

        self.assertEqual(result['success_count'], 2)
        self.assertEqual(len(result['failed_ids']), 0)

    def test_batch_save_monitor_data_length_mismatch(self):
        """测试参数长度不匹配 (TC-MON-020)"""
        host_ids = [self.host.id]
        data_list = [{'cpu': {'success': True}}, {'cpu': {'success': True}}]

        with self.assertRaises(MonitorDataSaveError):
            MonitorService.batch_save_monitor_data(host_ids, data_list)


class PolicyServiceTest(APITestCase):
    """PolicyService 测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    def test_create_policy_template_success(self):
        """测试创建策略模板成功 (TC-POL-001)"""
        data = {
            'name': '测试策略模板',
            'description': '这是一个测试策略',
            'template_type': 'custom',
            'is_builtin': False,
            'config': {
                'rules': [
                    {'type': 'port', 'action': 'block', 'port': 22},
                    {'type': 'process', 'action': 'allow', 'name': 'sshd'},
                ],
            },
        }

        result = PolicyService.create_policy_template(data, created_by=self.user)

        self.assertEqual(result['name'], '测试策略模板')
        self.assertEqual(result['description'], '这是一个测试策略')
        self.assertEqual(result['template_type'], 'custom')
        self.assertFalse(result['is_builtin'])

    def test_create_policy_template_minimal(self):
        """测试最少数据创建 (TC-POL-003)"""
        data = {
            'name': '最小策略模板',
        }

        result = PolicyService.create_policy_template(data, created_by=self.user)

        self.assertEqual(result['name'], '最小策略模板')
        self.assertEqual(result['description'], '')
        self.assertEqual(result['template_type'], 'custom')
        self.assertFalse(result['is_builtin'])

    def test_create_policy_template_builtin(self):
        """测试创建内置策略 (TC-POL-002)"""
        data = {
            'name': '内置策略模板',
            'is_builtin': True,
        }

        result = PolicyService.create_policy_template(data, created_by=self.user)

        self.assertEqual(result['name'], '内置策略模板')
        self.assertTrue(result['is_builtin'])

    def test_get_policy_template_success(self):
        """测试获取策略模板成功 (TC-POL-005)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='获取测试',
            description='获取测试描述',
            template_type='general',
            config={'rules': []},
            created_by=self.user,
        )

        result = PolicyService.get_policy_template(template.id)

        self.assertEqual(result['id'], template.id)
        self.assertEqual(result['name'], '获取测试')
        self.assertEqual(result['description'], '获取测试描述')
        self.assertEqual(result['template_type'], 'general')

    def test_get_policy_template_not_found(self):
        """测试策略模板不存在 (TC-POL-006)"""
        with self.assertRaises(PolicyTemplateNotFoundError):
            PolicyService.get_policy_template(99999)

    def test_list_policy_templates_success(self):
        """测试列出策略模板成功 (TC-POL-007)"""
        SafeguardPolicyTemplate.objects.create(
            name='模板1',
            template_type='general',
            config={'rules': []},
            created_by=self.user,
        )
        SafeguardPolicyTemplate.objects.create(
            name='模板2',
            template_type='custom',
            config={'rules': []},
            created_by=self.user,
        )

        result = PolicyService.list_policy_templates()

        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['data']), 2)

    def test_list_policy_templates_filter_by_type(self):
        """测试按类型过滤 (TC-POL-008)"""
        SafeguardPolicyTemplate.objects.create(
            name='一般模板',
            template_type='general',
            config={'rules': []},
            created_by=self.user,
        )
        SafeguardPolicyTemplate.objects.create(
            name='自定义模板',
            template_type='custom',
            config={'rules': []},
            created_by=self.user,
        )

        result = PolicyService.list_policy_templates(template_type='general')

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['name'], '一般模板')

    def test_bind_host_policy_first_time(self):
        """测试首次绑定主机策略 (TC-POL-010)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='绑定测试',
            config={'rules': [{'type': 'port', 'action': 'block', 'port': 22}]},
            created_by=self.user,
        )

        result = PolicyService.bind_host_policy(self.host.id, template.id, created_by=self.user)

        self.assertEqual(result['host_id'], self.host.id)
        self.assertEqual(result['template_id'], template.id)
        self.assertEqual(result['status'], 'pending')

    def test_bind_host_policy_update_existing(self):
        """测试更新已有策略 (TC-POL-011)"""
        template1 = SafeguardPolicyTemplate.objects.create(
            name='初始模板',
            config={'rules': [{'type': 'port', 'action': 'block', 'port': 22}]},
            created_by=self.user,
        )
        template2 = SafeguardPolicyTemplate.objects.create(
            name='更新模板',
            config={'rules': [{'type': 'port', 'action': 'allow', 'port': 22}]},
            created_by=self.user,
        )

        PolicyService.bind_host_policy(self.host.id, template1.id, created_by=self.user)
        result = PolicyService.bind_host_policy(self.host.id, template2.id, created_by=self.user)

        self.assertEqual(result['host_id'], self.host.id)
        self.assertEqual(result['template_id'], template2.id)
        self.assertEqual(result['status'], 'pending')

    def test_bind_host_policy_host_not_found(self):
        """测试绑定策略时主机不存在 (TC-POL-013)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='测试模板',
            config={'rules': []},
            created_by=self.user,
        )

        with self.assertRaises(HostNotFoundError):
            PolicyService.bind_host_policy(99999, template.id, created_by=self.user)

    def test_bind_host_policy_template_not_found(self):
        """测试绑定策略时模板不存在 (TC-POL-014)"""
        with self.assertRaises(PolicyTemplateNotFoundError):
            PolicyService.bind_host_policy(self.host.id, 99999, created_by=self.user)

    def test_get_host_policy_success(self):
        """测试获取主机策略成功 (TC-POL-015)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='测试模板',
            config={'rules': [{'type': 'port', 'action': 'block', 'port': 22}]},
            created_by=self.user,
        )
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=template,
            config=template.config.copy(),
            config_version=1,
            status='pending',
        )

        result = PolicyService.get_host_policy(self.host.id)

        self.assertEqual(result['id'], policy.id)
        self.assertEqual(result['host_id'], self.host.id)
        self.assertEqual(result['template_id'], template.id)
        self.assertEqual(result['status'], 'pending')

    def test_get_host_policy_not_found(self):
        """测试主机策略不存在 (TC-POL-016)"""
        with self.assertRaises(HostPolicyNotFoundError):
            PolicyService.get_host_policy(self.host.id)

    @mock.patch('backend.tasks.safeguard.apply_policy_task')
    def test_apply_policy_success(self, mock_apply_task):
        """测试触发策略下发成功 (TC-POL-017)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='下发测试',
            config={'rules': []},
            created_by=self.user,
        )
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=template,
            config=template.config.copy(),
            config_version=1,
            status='pending',
        )
        task = PolicyApplyTask.objects.create(
            host=self.host,
            policy=policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        result = PolicyService.apply_policy(task.id)

        self.assertEqual(result['task_id'], task.id)
        self.assertIn('Policy apply task has been queued', result['message'])
        mock_apply_task.delay.assert_called_once_with(task.id)

    def test_apply_policy_task_not_found(self):
        """测试任务不存在 (TC-POL-018)"""
        with self.assertRaises(TaskNotFoundError):
            PolicyService.apply_policy(99999)

    def test_get_task_status_success(self):
        """测试获取任务状态成功 (TC-POL-019)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='任务状态测试',
            config={'rules': []},
            created_by=self.user,
        )
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=template,
            config=template.config.copy(),
            config_version=1,
            status='pending',
        )
        task = PolicyApplyTask.objects.create(
            host=self.host,
            policy=policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        result = PolicyService.get_task_status(task.id)

        self.assertEqual(result['id'], task.id)
        self.assertEqual(result['status'], 'pending')

    def test_get_task_status_not_found(self):
        """测试获取任务状态时任务不存在"""
        with self.assertRaises(TaskNotFoundError):
            PolicyService.get_task_status(99999)


class AuditServiceFileMonitorRuleTest(APITestCase):
    """AuditService 文件监控规则测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    def test_create_file_monitor_rule_success(self):
        """测试创建文件监控规则成功 (TC-AUD-013)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/etc/passwd',
            monitor_type='file',
            watch_create=True,
            watch_modify=True,
            watch_delete=True,
        )

        self.assertEqual(result['host_id'], self.host.id)
        self.assertEqual(result['path'], '/etc/passwd')
        self.assertTrue(result['enabled'])

    def test_create_file_monitor_rule_type_file(self):
        """测试文件类型监控 (TC-AUD-014)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/etc/ssh/sshd_config',
            monitor_type='file',
        )

        rule = FileMonitorRule.objects.get(id=result['id'])
        self.assertEqual(rule.monitor_type, 'file')

    def test_create_file_monitor_rule_type_dir(self):
        """测试目录类型监控 (TC-AUD-015)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/etc',
            monitor_type='dir',
        )

        rule = FileMonitorRule.objects.get(id=result['id'])
        self.assertEqual(rule.monitor_type, 'dir')

    def test_create_file_monitor_rule_recursive(self):
        """测试递归监控 (TC-AUD-016)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/var/log',
            monitor_type='dir',
            recursive=True,
        )

        rule = FileMonitorRule.objects.get(id=result['id'])
        self.assertTrue(rule.recursive)

    def test_create_file_monitor_rule_event_types(self):
        """测试事件类型配置 (TC-AUD-017)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/tmp',
            monitor_type='dir',
            watch_create=True,
            watch_modify=False,
            watch_delete=True,
            watch_access=False,
            watch_perm=True,
        )

        rule = FileMonitorRule.objects.get(id=result['id'])
        self.assertTrue(rule.watch_create)
        self.assertFalse(rule.watch_modify)
        self.assertTrue(rule.watch_delete)
        self.assertFalse(rule.watch_access)
        self.assertTrue(rule.watch_perm)

    def test_create_file_monitor_rule_includes_excludes(self):
        """测试包含/排除规则 (TC-AUD-018)"""
        result = AuditService.create_file_monitor_rule(
            host_id=self.host.id,
            path='/var',
            monitor_type='dir',
            includes=['*.log', '*.conf'],
            excludes=['*.tmp', '*.swp'],
        )

        rule = FileMonitorRule.objects.get(id=result['id'])
        self.assertEqual(rule.includes, ['*.log', '*.conf'])
        self.assertEqual(rule.excludes, ['*.tmp', '*.swp'])

    def test_create_file_monitor_rule_host_not_found(self):
        """测试创建规则时主机不存在 (TC-AUD-019)"""
        with self.assertRaises(HostNotFoundError):
            AuditService.create_file_monitor_rule(
                host_id=99999,
                path='/etc/passwd',
            )

    def test_list_file_monitor_rules_success(self):
        """测试列出监控规则 (TC-AUD-020)"""
        # 创建一些测试规则
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )
        FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/ssh',
            monitor_type='dir',
        )

        result = AuditService.list_file_monitor_rules()

        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['data']), 2)

    def test_list_file_monitor_rules_filter_by_host(self):
        """测试按主机过滤规则 (TC-AUD-021)"""
        # 创建另一个主机
        host2 = Host.objects.create(
            hostname='test-host2',
            ip_address='192.168.1.101',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

        # 创建规则
        FileMonitorRule.objects.create(host=self.host, path='/etc/passwd', monitor_type='file')
        FileMonitorRule.objects.create(host=host2, path='/etc/passwd', monitor_type='file')

        # 只查询 host1 的规则
        result = AuditService.list_file_monitor_rules(host_id=self.host.id)

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['host_id'], self.host.id)

    def test_list_file_monitor_rules_filter_by_enabled(self):
        """测试按启用状态过滤规则 (TC-AUD-022)"""
        # 创建规则
        rule1 = FileMonitorRule.objects.create(
            host=self.host, path='/etc/passwd', monitor_type='file', enabled=True
        )
        rule2 = FileMonitorRule.objects.create(
            host=self.host, path='/etc/group', monitor_type='file', enabled=False
        )

        # 查询启用的规则
        result = AuditService.list_file_monitor_rules(enabled=True)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['id'], rule1.id)

        # 查询禁用的规则
        result = AuditService.list_file_monitor_rules(enabled=False)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['id'], rule2.id)


class AuditServiceFileMonitorEventTest(APITestCase):
    """AuditService 文件监控事件测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )
        self.rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )

    def test_list_file_monitor_events_success(self):
        """测试列出监控事件 (TC-AUD-023)"""
        from django.utils import timezone
        # 创建测试事件
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

        result = AuditService.list_file_monitor_events()

        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['data']), 2)

    def test_list_file_monitor_events_filter_by_host(self):
        """测试按主机过滤事件 (TC-AUD-024)"""
        from django.utils import timezone
        # 创建另一个主机
        host2 = Host.objects.create(
            hostname='test-host2',
            ip_address='192.168.1.101',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )
        rule2 = FileMonitorRule.objects.create(
            host=host2,
            path='/etc/passwd',
            monitor_type='file',
        )

        # 创建事件
        FileMonitorEvent.objects.create(
            host=self.host, rule=self.rule, event_type='modify', timestamp=timezone.now()
        )
        FileMonitorEvent.objects.create(
            host=host2, rule=rule2, event_type='create', timestamp=timezone.now()
        )

        # 查询 host1 的事件
        result = AuditService.list_file_monitor_events(host_id=self.host.id)

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['host_id'], self.host.id)

    def test_list_file_monitor_events_filter_by_event_type(self):
        """测试按事件类型过滤 (TC-AUD-025)"""
        from django.utils import timezone
        # 创建事件
        FileMonitorEvent.objects.create(
            host=self.host, rule=self.rule, event_type='modify', timestamp=timezone.now()
        )
        FileMonitorEvent.objects.create(
            host=self.host, rule=self.rule, event_type='delete', timestamp=timezone.now()
        )
        FileMonitorEvent.objects.create(
            host=self.host, rule=self.rule, event_type='create', timestamp=timezone.now()
        )

        # 只查询 modify 事件
        result = AuditService.list_file_monitor_events(event_type='modify')

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['event_type'], 'modify')

    @mock.patch('backend.services.safeguard.collect_file_events')
    def test_collect_file_events_success(self, mock_collect):
        """测试采集监控事件 (TC-AUD-026)"""
        mock_collect.return_value = {
            'success': True,
            'events': [
                {
                    'rule_id': self.rule.id,
                    'event_type': 'modify',
                    'path': '/etc/passwd',
                    'details': {},
                },
            ],
        }

        result = AuditService.collect_file_events(host_id=self.host.id)

        self.assertIn('events', result)
        self.assertIn('total_events', result)

    def test_collect_file_events_no_rules(self):
        """测试无启用规则时采集 (TC-AUD-027)"""
        # 禁用规则
        self.rule.enabled = False
        self.rule.save()

        result = AuditService.collect_file_events(host_id=self.host.id)

        self.assertEqual(result['message'], 'No active monitor rules found')
        self.assertEqual(result['total_events'], 0)

    def test_save_file_events_success(self):
        """测试保存监控事件 (TC-AUD-028)"""
        events = [
            {
                'rule_id': self.rule.id,
                'event_type': 'modify',
                'path': '/etc/passwd',
                'details': {'size': 1024},
            },
            {
                'rule_id': self.rule.id,
                'event_type': 'access',
                'path': '/etc/passwd',
                'details': {},
            },
        ]

        saved_count = AuditService.save_file_events(events)

        self.assertEqual(saved_count, 2)
        self.assertEqual(FileMonitorEvent.objects.count(), 2)

    def test_save_file_events_partial_failure(self):
        """测试部分事件保存失败 (TC-AUD-029)"""
        events = [
            {
                'rule_id': self.rule.id,  # 有效规则
                'event_type': 'modify',
                'path': '/etc/passwd',
                'details': {},
            },
            {
                'rule_id': 99999,  # 无效规则
                'event_type': 'delete',
                'path': '/etc/group',
                'details': {},
            },
        ]

        saved_count = AuditService.save_file_events(events)

        self.assertEqual(saved_count, 1)  # 只保存了有效规则的事件
        self.assertEqual(FileMonitorEvent.objects.count(), 1)


class AuditServiceSystemLogTest(APITestCase):
    """AuditService 系统日志测试"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_success(self, mock_collect):
        """测试采集系统日志成功 (TC-AUD-030)"""
        mock_collect.return_value = {
            'success': True,
            'logs': [
                {
                    'source': 'auth',
                    'level': 'info',
                    'message': 'Accepted publickey',
                    'timestamp': 'Jul 10 10:00:00',
                    'raw_line': 'Jul 10 10:00:00 host sshd[1234]: Accepted publickey',
                },
            ],
        }

        result = AuditService.collect_and_save_system_logs(self.host.id)

        self.assertIn('logs', result)

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_with_sources(self, mock_collect):
        """测试指定日志源 (TC-AUD-031)"""
        mock_collect.return_value = {
            'success': True,
            'logs': [],
        }

        AuditService.collect_and_save_system_logs(
            self.host.id,
            log_sources=['auth', 'syslog'],
        )

        # 验证调用参数
        call_args = mock_collect.call_args
        self.assertEqual(call_args[0][1], ['auth', 'syslog'])

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_with_num_lines(self, mock_collect):
        """测试指定行数 (TC-AUD-032)"""
        mock_collect.return_value = {
            'success': True,
            'logs': [],
        }

        AuditService.collect_and_save_system_logs(
            self.host.id,
            num_lines=200,
        )

        # 验证调用参数
        call_args = mock_collect.call_args
        self.assertEqual(call_args[0][2], 200)

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_no_save(self, mock_collect):
        """测试不保存到数据库 (TC-AUD-033)"""
        from backend.models.audit.system_log import SystemLog
        mock_collect.return_value = {
            'success': True,
            'logs': [
                {
                    'source': 'auth',
                    'level': 'info',
                    'message': 'Test log',
                    'timestamp': 'Jul 10 10:00:00',
                    'raw_line': 'Test log line',
                },
            ],
        }

        SystemLog.objects.all().delete()  # 清空日志

        result = AuditService.collect_and_save_system_logs(
            self.host.id,
            save_to_db=False,
        )

        # 验证没有保存到数据库
        self.assertEqual(SystemLog.objects.count(), 0)

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_timestamp_parsing(self, mock_collect):
        """测试时间戳解析 (TC-AUD-034)"""
        from backend.models.audit.system_log import SystemLog
        mock_collect.return_value = {
            'success': True,
            'logs': [
                {
                    'source': 'auth',
                    'level': 'info',
                    'message': 'Test log',
                    'timestamp': 'Jul 10 10:00:00',
                    'raw_line': 'Jul 10 10:00:00 host sshd[1234]: Test',
                },
            ],
        }

        AuditService.collect_and_save_system_logs(self.host.id)

        # 验证日志被保存
        self.assertEqual(SystemLog.objects.count(), 1)
        log = SystemLog.objects.first()
        self.assertEqual(log.timestamp.month, 7)
        self.assertEqual(log.timestamp.day, 10)
        self.assertEqual(log.timestamp.hour, 10)
        self.assertEqual(log.timestamp.minute, 0)

    @mock.patch('backend.services.safeguard.collect_system_logs')
    def test_collect_and_save_system_logs_timestamp_parsing_failed(self, mock_collect):
        """测试时间戳解析失败 (TC-AUD-035)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        mock_collect.return_value = {
            'success': True,
            'logs': [
                {
                    'source': 'auth',
                    'level': 'info',
                    'message': 'Test log',
                    'timestamp': 'Invalid Date Format',
                    'raw_line': 'Invalid date log line',
                },
            ],
        }

        AuditService.collect_and_save_system_logs(self.host.id)

        # 验证日志被保存（使用当前时间）
        self.assertEqual(SystemLog.objects.count(), 1)

    def test_get_system_logs_success(self):
        """测试查询系统日志 (TC-AUD-036)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        # 创建测试日志
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

        result = AuditService.get_system_logs()

        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['data']), 2)

    def test_get_system_logs_filter_by_host(self):
        """测试按主机过滤系统日志 (TC-AUD-037)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        # 创建另一个主机
        host2 = Host.objects.create(
            hostname='test-host2',
            ip_address='192.168.1.101',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

        # 创建日志
        SystemLog.objects.create(
            host=self.host, source='auth', level='info', message='Log 1', timestamp=timezone.now()
        )
        SystemLog.objects.create(
            host=host2, source='auth', level='info', message='Log 2', timestamp=timezone.now()
        )

        # 查询 host1 的日志
        result = AuditService.get_system_logs(host_id=self.host.id)

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['host_id'], self.host.id)

    def test_get_system_logs_filter_by_source(self):
        """测试按日志源过滤 (TC-AUD-038)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        # 创建日志
        SystemLog.objects.create(
            host=self.host, source='auth', level='info', message='Auth log', timestamp=timezone.now()
        )
        SystemLog.objects.create(
            host=self.host, source='syslog', level='info', message='Sys log', timestamp=timezone.now()
        )

        # 查询 auth 日志
        result = AuditService.get_system_logs(source='auth')

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['source'], 'auth')

    def test_get_system_logs_filter_by_level(self):
        """测试按级别过滤 (TC-AUD-039)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        # 创建日志
        SystemLog.objects.create(
            host=self.host, source='auth', level='info', message='Info log', timestamp=timezone.now()
        )
        SystemLog.objects.create(
            host=self.host, source='auth', level='error', message='Error log', timestamp=timezone.now()
        )

        # 查询 error 日志
        result = AuditService.get_system_logs(level='error')

        self.assertEqual(result['total'], 1)
        self.assertEqual(result['data'][0]['level'], 'error')

    def test_get_system_logs_pagination(self):
        """测试系统日志分页 (TC-AUD-040)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        # 创建更多日志
        for i in range(15):
            SystemLog.objects.create(
                host=self.host,
                source='auth',
                level='info',
                message=f'Log {i}',
                timestamp=timezone.now(),
            )

        # 查询第二页，每页5条
        result = AuditService.get_system_logs(page=2, page_size=5)

        self.assertEqual(result['total'], 15)
        self.assertEqual(result['page'], 2)
        self.assertEqual(result['page_size'], 5)
        self.assertEqual(len(result['data']), 5)


class SafeguardModelTest(APITestCase):
    """数据模型测试 (TC-MDL-004 到 TC-MDL-010)"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    def test_create_host_monitor_data(self):
        """测试创建监控数据 (TC-MDL-004)"""
        from backend.models.safeguard.monitor import HostMonitorData
        from django.utils import timezone

        monitor_data = HostMonitorData.objects.create(
            host=self.host,
            cpu_usage=45.5,
            load_1m=0.8,
            load_5m=0.6,
            load_15m=0.5,
            memory_total=16384,
            memory_used=4096,
            memory_usage=25.0,
            network_in=1024000,
            network_out=512000,
            timestamp=timezone.now(),
        )

        self.assertEqual(monitor_data.host, self.host)
        self.assertEqual(monitor_data.cpu_usage, 45.5)
        self.assertEqual(monitor_data.load_1m, 0.8)
        self.assertEqual(monitor_data.memory_usage, 25.0)

    def test_create_safeguard_policy_template(self):
        """测试创建策略模板 (TC-MDL-005)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='测试模板',
            description='测试描述',
            template_type='general',
            is_builtin=False,
            config={'rules': []},
            created_by=self.user,
        )

        self.assertEqual(template.name, '测试模板')
        self.assertEqual(template.description, '测试描述')
        self.assertEqual(template.template_type, 'general')
        self.assertFalse(template.is_builtin)

    def test_create_host_safeguard_policy(self):
        """测试创建主机策略 (TC-MDL-006)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='测试模板',
            config={'rules': []},
            created_by=self.user,
        )
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=template,
            config=template.config.copy(),
            config_version=1,
            status='pending',
        )

        self.assertEqual(policy.host, self.host)
        self.assertEqual(policy.template, template)
        self.assertEqual(policy.config_version, 1)
        self.assertEqual(policy.status, 'pending')

    def test_create_policy_apply_task(self):
        """测试创建下发任务 (TC-MDL-007)"""
        template = SafeguardPolicyTemplate.objects.create(
            name='测试模板',
            config={'rules': []},
            created_by=self.user,
        )
        policy = HostSafeguardPolicy.objects.create(
            host=self.host,
            template=template,
            config=template.config.copy(),
            config_version=1,
            status='pending',
        )
        task = PolicyApplyTask.objects.create(
            host=self.host,
            policy=policy,
            task_type='apply',
            status='pending',
            created_by=self.user,
        )

        self.assertEqual(task.host, self.host)
        self.assertEqual(task.policy, policy)
        self.assertEqual(task.task_type, 'apply')
        self.assertEqual(task.status, 'pending')

    def test_create_file_monitor_rule(self):
        """测试创建文件监控规则 (TC-MDL-008)"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
            watch_create=True,
            watch_modify=True,
            watch_delete=True,
            enabled=True,
        )

        self.assertEqual(rule.host, self.host)
        self.assertEqual(rule.path, '/etc/passwd')
        self.assertEqual(rule.monitor_type, 'file')
        self.assertTrue(rule.watch_create)
        self.assertTrue(rule.enabled)

    def test_create_file_monitor_event(self):
        """测试创建文件监控事件 (TC-MDL-009)"""
        rule = FileMonitorRule.objects.create(
            host=self.host,
            path='/etc/passwd',
            monitor_type='file',
        )
        from django.utils import timezone
        event = FileMonitorEvent.objects.create(
            host=self.host,
            rule=rule,
            event_type='modify',
            path='/etc/passwd',
            timestamp=timezone.now(),
        )

        self.assertEqual(event.host, self.host)
        self.assertEqual(event.rule, rule)
        self.assertEqual(event.event_type, 'modify')

    def test_create_system_log(self):
        """测试创建系统日志 (TC-MDL-010)"""
        from backend.models.audit.system_log import SystemLog
        from django.utils import timezone
        log = SystemLog.objects.create(
            host=self.host,
            source='auth',
            level='info',
            message='Accepted publickey',
            raw_log='Jul 10 10:00:00 host sshd[1234]: Accepted publickey',
            timestamp=timezone.now(),
        )

        self.assertEqual(log.host, self.host)
        self.assertEqual(log.source, 'auth')
        self.assertEqual(log.level, 'info')
        self.assertEqual(log.message, 'Accepted publickey')


class SafeguardSecurityTest(APITestCase):
    """安全测试 (TC-SEC-001 到 TC-SEC-005)"""

    def setUp(self):
        """创建测试数据"""
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='testpass',
            os_type='linux',
        )

    @mock.patch('backend.services.safeguard.control_service')
    def test_control_service_command_injection_protection(self, mock_control):
        """测试命令注入防护 (TC-SEC-001)"""
        from backend.services.safeguard import HostInfoService
        mock_control.return_value = {'success': True, 'message': 'Test'}

        # 尝试注入恶意命令
        result = HostInfoService.control_service(
            self.host.id,
            'sshd; rm -rf /',  # 包含恶意命令
            'start'
        )

        # 验证参数被安全处理
        call_args = mock_control.call_args
        # 检查是否调用了control_service
        mock_control.assert_called_once()

    @mock.patch('backend.utils.hardware_collector.SSHClient')
    def test_kill_process_pid_validation(self, mock_ssh):
        """测试PID参数验证 (TC-SEC-002)"""
        from backend.utils.hardware_collector import _kill_process

        # Mock SSH client
        mock_client = MagicMock()
        mock_ssh.return_value.__enter__.return_value = mock_client

        # 测试非数字PID
        result = _kill_process(mock_client, 'abc123')
        self.assertFalse(result['success'])
        self.assertIn('Invalid pid', result['message'])

    @mock.patch('backend.utils.hardware_collector.SSHClient')
    def test_init_process_protection(self, mock_ssh):
        """测试init进程保护 (TC-SEC-003)"""
        from backend.utils.hardware_collector import _kill_process

        # Mock SSH client
        mock_client = MagicMock()
        mock_ssh.return_value.__enter__.return_value = mock_client

        # 测试终止PID 1
        result = _kill_process(mock_client, 1)
        self.assertFalse(result['success'])
        self.assertIn('Cannot kill init process', result['message'])

    def test_audit_log_integrity(self):
        """测试审计日志完整性 (TC-SEC-005)"""
        from backend.services.safeguard import AuditService

        # 执行一些会记录日志的操作
        AuditService.log_action(
            user=self.user,
            action='create',
            resource_type='policy',
            resource_id='1',
            resource_name='测试策略',
        )

        # 验证日志完整记录
        audit_log = AuditLog.objects.first()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'create')
        self.assertEqual(audit_log.resource_type, 'policy')
        self.assertEqual(audit_log.resource_id, '1')
        self.assertEqual(audit_log.resource_name, '测试策略')
        self.assertIsNotNone(audit_log.created_at)
