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
