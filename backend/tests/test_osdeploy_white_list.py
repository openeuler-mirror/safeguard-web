from django.test import TestCase

from backend.models.osdeploy.white_list import WhiteList


class WhiteListModelTest(TestCase):
    """WhiteList 模型测试"""

    def test_create_white_list(self):
        """测试创建白名单"""
        wl = WhiteList.objects.create(
            mac_address='00:0c:29:12:34:56',
            hostname='server-001',
            ip_address='192.168.1.100'
        )
        self.assertEqual(wl.mac_address, '00:0c:29:12:34:56')
        self.assertEqual(wl.hostname, 'server-001')
        self.assertEqual(wl.ip_address, '192.168.1.100')

    def test_white_list_str(self):
        """测试白名单字符串表示"""
        wl = WhiteList(mac_address='00:0c:29:12:34:56', hostname='test-host')
        self.assertEqual(str(wl), 'test-host - 00:0c:29:12:34:56')

    def test_white_list_str_without_hostname(self):
        """测试无主机名的白名单字符串表示"""
        wl = WhiteList(mac_address='00:0c:29:12:34:56', hostname='')
        self.assertEqual(str(wl), 'Unknown - 00:0c:29:12:34:56')

    def test_white_list_mac_unique(self):
        """测试MAC地址唯一性"""
        WhiteList.objects.create(
            mac_address='aa:bb:cc:dd:ee:ff',
            hostname='host1'
        )
        with self.assertRaises(Exception):
            WhiteList.objects.create(
                mac_address='aa:bb:cc:dd:ee:ff',
                hostname='host2'
            )

    def test_white_list_default_values(self):
        """测试白名单默认值"""
        wl = WhiteList.objects.create(
            mac_address='11:22:33:44:55:66'
        )
        self.assertEqual(wl.hostname, '')
        self.assertIsNone(wl.ip_address)
        self.assertEqual(wl.description, '')
        self.assertTrue(wl.is_active)

    def test_white_list_is_active(self):
        """测试白名单激活状态"""
        wl1 = WhiteList.objects.create(
            mac_address='11:11:11:11:11:11',
            is_active=True
        )
        wl2 = WhiteList.objects.create(
            mac_address='22:22:22:22:22:22',
            is_active=False
        )
        self.assertTrue(wl1.is_active)
        self.assertFalse(wl2.is_active)

    def test_white_list_with_description(self):
        """测试白名单描述"""
        wl = WhiteList.objects.create(
            mac_address='33:33:33:33:33:33',
            description='Production server whitelist'
        )
        self.assertEqual(wl.description, 'Production server whitelist')

    def test_white_list_with_ip_address(self):
        """测试白名单IP地址"""
        wl = WhiteList.objects.create(
            mac_address='44:44:44:44:44:44',
            ip_address='10.0.0.50'
        )
        self.assertEqual(wl.ip_address, '10.0.0.50')

    def test_white_list_without_ip(self):
        """测试无IP的白名单"""
        wl = WhiteList.objects.create(
            mac_address='55:55:55:55:55:55',
            hostname='no-ip-host'
        )
        self.assertIsNone(wl.ip_address)

    def test_white_list_ordering(self):
        """测试白名单按ID顺序排列"""
        wl1 = WhiteList.objects.create(mac_address='66:66:66:66:66:66')
        wl2 = WhiteList.objects.create(mac_address='77:77:77:77:77:77')
        wls = WhiteList.objects.all()
        self.assertEqual(wls[0], wl1)
        self.assertEqual(wls[1], wl2)