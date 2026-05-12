from django.test import TestCase

from backend.models.osdeploy.out_ip_sn import OutIpSN


class OutIpSNModelTest(TestCase):
    """OutIpSN 模型测试"""

    def test_create_out_ip_sn(self):
        """测试创建出口IP序列号"""
        sn = OutIpSN.objects.create(
            mac_address='00:0c:29:12:34:56',
            sn='SN-2024-001'
        )
        self.assertEqual(sn.mac_address, '00:0c:29:12:34:56')
        self.assertEqual(sn.sn, 'SN-2024-001')

    def test_out_ip_sn_str(self):
        """测试出口IP序列号字符串表示"""
        sn = OutIpSN(mac_address='00:0c:29:12:34:56', sn='SN-001')
        self.assertEqual(str(sn), '00:0c:29:12:34:56 - SN-001')

    def test_out_ip_sn_mac_unique(self):
        """测试MAC地址唯一性"""
        OutIpSN.objects.create(
            mac_address='aa:bb:cc:dd:ee:ff',
            sn='SN-UNIQUE-1'
        )
        with self.assertRaises(Exception):
            OutIpSN.objects.create(
                mac_address='aa:bb:cc:dd:ee:ff',
                sn='SN-UNIQUE-2'
            )

    def test_out_ip_sn_default_values(self):
        """测试出口IP序列号默认值"""
        sn = OutIpSN.objects.create(
            mac_address='11:22:33:44:55:66',
            sn='SN-DEFAULT'
        )
        self.assertEqual(sn.description, '')

    def test_out_ip_sn_with_description(self):
        """测试出口IP序列号描述"""
        sn = OutIpSN.objects.create(
            mac_address='22:33:44:55:66:77',
            sn='SN-DESCRIBED',
            description='Reserved for external network'
        )
        self.assertEqual(sn.description, 'Reserved for external network')

    def test_out_ip_sn_ordering(self):
        """测试出口IP序列号按ID顺序排列"""
        sn1 = OutIpSN.objects.create(
            mac_address='33:44:55:66:77:88',
            sn='SN-ORDER-1'
        )
        sn2 = OutIpSN.objects.create(
            mac_address='44:55:66:77:88:99',
            sn='SN-ORDER-2'
        )
        sns = OutIpSN.objects.all()
        self.assertEqual(sns[0], sn1)
        self.assertEqual(sns[1], sn2)

    def test_out_ip_sn_multiple_records(self):
        """测试多条出口IP序列号记录"""
        macs = [
            ('00:01:02:03:04:05', 'SN-A'),
            ('00:01:02:03:04:06', 'SN-B'),
            ('00:01:02:03:04:07', 'SN-C'),
        ]
        for mac, sn_val in macs:
            OutIpSN.objects.create(mac_address=mac, sn=sn_val)
        self.assertEqual(OutIpSN.objects.count(), 3)