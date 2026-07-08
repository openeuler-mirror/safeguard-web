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
