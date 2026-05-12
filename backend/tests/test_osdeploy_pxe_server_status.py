from django.test import TestCase

from backend.models.osdeploy.pxe_server_status import PXEServerStatus


class PXEServerStatusModelTest(TestCase):
    """PXEServerStatus 模型测试"""

    def test_create_pxe_server_status(self):
        """测试创建PXE服务器状态"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.10',
            interface='eth0',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        self.assertEqual(pxe.server_ip, '192.168.1.10')
        self.assertEqual(pxe.interface, 'eth0')
        self.assertEqual(pxe.dhcp_range_start, '192.168.1.100')
        self.assertEqual(pxe.dhcp_range_end, '192.168.1.200')
        self.assertEqual(pxe.subnet, '255.255.255.0')
        self.assertEqual(pxe.gateway, '192.168.1.1')
        self.assertEqual(pxe.status, 'active')

    def test_pxe_server_status_str(self):
        """测试PXE服务器状态字符串表示"""
        pxe = PXEServerStatus(server_ip='192.168.1.20')
        self.assertEqual(str(pxe), 'PXE Server 192.168.1.20')

    def test_pxe_server_ip_unique(self):
        """测试PXE服务器IP唯一性"""
        PXEServerStatus.objects.create(
            server_ip='192.168.1.50',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1'
        )
        with self.assertRaises(Exception):
            PXEServerStatus.objects.create(
                server_ip='192.168.1.50',
                dhcp_range_start='192.168.2.100',
                dhcp_range_end='192.168.2.200',
                subnet='255.255.255.0',
                gateway='192.168.2.1'
            )

    def test_pxe_server_status_default_values(self):
        """测试PXE服务器状态默认值"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.60',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1'
        )
        self.assertEqual(pxe.interface, 'eth0')
        self.assertEqual(pxe.status, 'active')
        self.assertEqual(pxe.description, '')

    def test_pxe_server_status_all_status_choices(self):
        """测试PXE服务器所有状态选项"""
        for status_value, status_label in PXEServerStatus.STATUS_CHOICES:
            pxe = PXEServerStatus.objects.create(
                server_ip=f'192.168.{100 + PXEServerStatus.STATUS_CHOICES.index((status_value, status_label))}.10',
                dhcp_range_start=f'192.168.{100 + PXEServerStatus.STATUS_CHOICES.index((status_value, status_label))}.100',
                dhcp_range_end=f'192.168.{100 + PXEServerStatus.STATUS_CHOICES.index((status_value, status_label))}.200',
                subnet='255.255.255.0',
                gateway=f'192.168.{100 + PXEServerStatus.STATUS_CHOICES.index((status_value, status_label))}.1',
                status=status_value
            )
            self.assertEqual(pxe.status, status_value)

    def test_pxe_server_status_with_description(self):
        """测试PXE服务器描述"""
        pxe = PXEServerStatus.objects.create(
            server_ip='192.168.1.70',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            description='Primary PXE server for OS deployment'
        )
        self.assertEqual(pxe.description, 'Primary PXE server for OS deployment')

    def test_pxe_server_status_ordering(self):
        """测试PXE服务器按ID顺序排列"""
        pxe1 = PXEServerStatus.objects.create(
            server_ip='192.168.1.80',
            dhcp_range_start='192.168.1.100',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1'
        )
        pxe2 = PXEServerStatus.objects.create(
            server_ip='192.168.1.90',
            dhcp_range_start='192.168.2.100',
            dhcp_range_end='192.168.2.200',
            subnet='255.255.255.0',
            gateway='192.168.2.1'
        )
        pxes = PXEServerStatus.objects.all()
        self.assertEqual(pxes[0], pxe1)
        self.assertEqual(pxes[1], pxe2)