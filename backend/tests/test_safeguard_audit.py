"""
Test Safeguard Audit Middleware

测试审计日志中间件功能
"""
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.test import override_settings

from backend.models import Users
from backend.models.audit.audit_log import AuditLog


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


@override_settings(AUDIT_LOG_ENABLED=True)
class AuditLogMiddlewareTest(APITestCase):
    """审计日志中间件测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
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
        with override_settings(AUDIT_LOG_ENABLED=False):
            # 发送一个POST请求
            response = self.client.post('/api/users/', {
                'user': 'newuser',
                'password': 'newpass123',
                'nickname': '新用户'
            }, format='json')

            # 检查没有审计日志
            self.assertEqual(AuditLog.objects.count(), 0)

    def test_audit_log_get_request(self):
        """测试GET请求不记录审计日志"""
        response = self.client.get('/api/users/me/')

        # 检查没有审计日志
        self.assertEqual(AuditLog.objects.count(), 0)
