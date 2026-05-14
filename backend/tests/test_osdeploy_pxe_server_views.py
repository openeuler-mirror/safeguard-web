"""PXEServerStatus 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.osdeploy import PXEServerStatus


class PXEServerStatusViewSetTest(APITestCase):
    """PXEServerStatusViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_pxe',
            password='testpass123',
            nickname='测试用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_pxe_servers(self):
        """测试列出PXE服务器"""
        PXEServerStatus.objects.create(
            server_ip='192.168.1.10',
            interface='eth0',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        PXEServerStatus.objects.create(
            server_ip='192.168.1.11',
            interface='eth1',
            dhcp_range_start='192.168.2.100',
            dhcp_range_end='192.168.2.200',
            subnet='255.255.255.0',
            gateway='192.168.2.1',
            status='inactive'
        )
        response = self.client.get('/api/pxe-servers/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_pxe_server(self):
        """测试创建PXE服务器"""
        data = {
            'server_ip': '192.168.1.20',
            'interface': 'eth0',
            'dhcp_range_start': '192.168.1.150',
            'dhcp_range_end': '192.168.1.250',
            'subnet': '255.255.255.0',
            'gateway': '192.168.1.1',
            'status': 'active',
            'description': '新PXE服务器'
        }
        response = self.client.post('/api/pxe-servers/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['server_ip'], '192.168.1.20')

    def test_retrieve_pxe_server(self):
        """测试获取单个PXE服务器"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.30',
            interface='eth0',
            dhcp_range_start='192.168.1.150',
            dhcp_range_end='192.168.1.250',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        response = self.client.get(f'/api/pxe-servers/{pxe.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['server_ip'], '192.168.1.30')

    def test_update_pxe_server(self):
        """测试更新PXE服务器"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.40',
            interface='eth0',
            dhcp_range_start='192.168.1.150',
            dhcp_range_end='192.168.1.250',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        data = {
            'server_ip': '192.168.1.40',
            'interface': 'eth1',
            'dhcp_range_start': '192.168.2.150',
            'dhcp_range_end': '192.168.2.250',
            'subnet': '255.255.255.0',
            'gateway': '192.168.2.1',
            'status': 'inactive',
            'description': '更新后的PXE服务器'
        }
        response = self.client.put(f'/api/pxe-servers/{pxe.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['interface'], 'eth1')
        self.assertEqual(response.data['data']['status'], 'inactive')

    def test_partial_update_pxe_server(self):
        """测试部分更新PXE服务器"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.50',
            interface='eth0',
            dhcp_range_start='192.168.1.150',
            dhcp_range_end='192.168.1.250',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        data = {'status': 'inactive', 'description': '已停用'}
        response = self.client.patch(f'/api/pxe-servers/{pxe.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['status'], 'inactive')
        self.assertEqual(response.data['data']['description'], '已停用')

    def test_delete_pxe_server(self):
        """测试删除PXE服务器"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.60',
            interface='eth0',
            dhcp_range_start='192.168.1.150',
            dhcp_range_end='192.168.1.250',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        response = self.client.delete(f'/api/pxe-servers/{pxe.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(PXEServerStatus.objects.filter(pk=pxe.pk).exists())