"""DHCPService 测试"""
from django.test import TestCase
from backend.models.osdeploy import PXEServerStatus, WhiteList
from backend.services.osdeploy import DHCPService


class DHCPServiceTest(TestCase):
    """DHCPService 测试"""

    def setUp(self):
        self.pxe_server = PXEServerStatus.objects.create(
            server_ip='192.168.1.100',
            interface='eth0',
            dhcp_range_start='192.168.1.101',
            dhcp_range_end='192.168.1.200',
            subnet='255.255.255.0',
            gateway='192.168.1.1',
            status='active'
        )
        self.whitelist_entry = WhiteList.objects.create(
            mac_address='00:11:22:33:44:55',
            hostname='test-host',
            ip_address='192.168.1.50',
            is_active=True
        )

    def test_setup_dhcp(self):
        """测试配置DHCP服务"""
        # 先删除可能存在的记录
        PXEServerStatus.objects.filter(server_ip='192.168.1.101').delete()

        pxe = DHCPService.setup_dhcp(
            server_ip='192.168.1.101',
            interface='eth1',
            range_start='192.168.1.110',
            range_end='192.168.1.199',
            subnet='255.255.255.0',
            gateway='192.168.1.254'
        )
        self.assertEqual(pxe.server_ip, '192.168.1.101')
        self.assertEqual(pxe.interface, 'eth1')
        self.assertEqual(pxe.status, 'active')

    def test_setup_dhcp_update_existing(self):
        """测试更新已有的DHCP配置"""
        pxe = DHCPService.setup_dhcp(
            server_ip='192.168.1.100',
            interface='eth2',
            range_start='192.168.1.150',
            range_end='192.168.1.250'
        )
        self.assertEqual(pxe.interface, 'eth2')
        self.assertEqual(pxe.dhcp_range_start, '192.168.1.150')
        self.assertEqual(pxe.dhcp_range_end, '192.168.1.250')

    def test_add_static_entry(self):
        """测试添加静态DHCP条目"""
        # 先删除可能存在的记录
        WhiteList.objects.filter(mac_address='AA:BB:CC:DD:EE:FF').delete()

        entry = DHCPService.add_static_entry(
            mac='AA:BB:CC:DD:EE:FF',
            ip='192.168.1.60',
            hostname='new-host'
        )
        self.assertEqual(entry.mac_address, 'AA:BB:CC:DD:EE:FF')
        self.assertEqual(entry.ip_address, '192.168.1.60')
        self.assertEqual(entry.hostname, 'new-host')
        self.assertTrue(entry.is_active)

    def test_add_static_entry_update_existing(self):
        """测试更新已有的静态条目"""
        entry = DHCPService.add_static_entry(
            mac='00:11:22:33:44:55',
            ip='192.168.1.99',
            hostname='updated-host'
        )
        self.assertEqual(entry.ip_address, '192.168.1.99')
        self.assertEqual(entry.hostname, 'updated-host')

    def test_remove_static_entry(self):
        """测试移除静态DHCP条目"""
        result = DHCPService.remove_static_entry('00:11:22:33:44:55')
        self.assertTrue(result)
        self.assertFalse(WhiteList.objects.filter(mac_address='00:11:22:33:44:55').exists())

    def test_remove_static_entry_not_found(self):
        """测试移除不存在的静态条目"""
        result = DHCPService.remove_static_entry('FF:FF:FF:FF:FF:FF')
        self.assertFalse(result)

    def test_list_static_entries(self):
        """测试获取静态条目列表"""
        result = DHCPService.list_static_entries()
        self.assertEqual(result['total'], 1)

    def test_list_static_entries_with_pagination(self):
        """测试静态条目列表分页"""
        for i in range(15):
            WhiteList.objects.create(
                mac_address=f'00:00:00:00:00:{i:02x}',
                hostname=f'host{i}',
                ip_address=f'192.168.1.{i+100}'
            )
        result = DHCPService.list_static_entries(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_get_pxe_server(self):
        """测试获取PXE服务器"""
        pxe = DHCPService.get_pxe_server('192.168.1.100')
        self.assertIsNotNone(pxe)
        self.assertEqual(pxe.server_ip, '192.168.1.100')

    def test_get_pxe_server_not_found(self):
        """测试获取不存在的PXE服务器"""
        pxe = DHCPService.get_pxe_server('192.168.99.99')
        self.assertIsNone(pxe)

    def test_get_pxe_server_active_first(self):
        """测试获取第一个活跃的PXE服务器"""
        pxe = DHCPService.get_pxe_server()
        self.assertIsNotNone(pxe)
        self.assertEqual(pxe.status, 'active')

    def test_list_pxe_servers(self):
        """测试获取PXE服务器列表"""
        result = DHCPService.list_pxe_servers()
        self.assertEqual(result['total'], 1)

    def test_list_pxe_servers_with_pagination(self):
        """测试PXE服务器列表分页"""
        for i in range(15):
            PXEServerStatus.objects.create(
                server_ip=f'192.168.2.{i+1}',
                interface='eth0',
                dhcp_range_start=f'192.168.2.{i+10}',
                dhcp_range_end=f'192.168.2.{i+20}'
            )
        result = DHCPService.list_pxe_servers(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_validate_mac_address_valid(self):
        """测试验证有效的MAC地址"""
        self.assertTrue(DHCPService.validate_mac_address('00:11:22:33:44:55'))
        self.assertTrue(DHCPService.validate_mac_address('AA:BB:CC:DD:EE:FF'))
        self.assertTrue(DHCPService.validate_mac_address('00-11-22-33-44-55'))

    def test_validate_mac_address_invalid(self):
        """测试验证无效的MAC地址"""
        self.assertFalse(DHCPService.validate_mac_address('invalid'))
        self.assertFalse(DHCPService.validate_mac_address('00:11:22:33:44'))
        self.assertFalse(DHCPService.validate_mac_address('00:11:22:33:44:55:66'))

    def test_validate_ip_address_valid(self):
        """测试验证有效的IP地址"""
        self.assertTrue(DHCPService.validate_ip_address('192.168.1.1'))
        self.assertTrue(DHCPService.validate_ip_address('10.0.0.1'))
        self.assertTrue(DHCPService.validate_ip_address('255.255.255.255'))

    def test_validate_ip_address_invalid(self):
        """测试验证无效的IP地址"""
        self.assertFalse(DHCPService.validate_ip_address('invalid'))
        self.assertFalse(DHCPService.validate_ip_address('192.168.1'))
        self.assertFalse(DHCPService.validate_ip_address('192.168.1.256'))
