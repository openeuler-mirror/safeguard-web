"""
硬件信息采集工具单元测试
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from backend.utils.hardware_collector import (
    collect_host_hardware,
    collect_host_lldp,
    update_host_hardware_info,
    update_host_lldp_info,
    collect_all_hardware_info,
)


class MockHost:
    """模拟 Host 模型"""
    def __init__(self, id=1, ip_address="192.168.1.100", port=22,
                 username="root", password="password"):
        self.id = id
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.arch_info = ''
        self.uptime = ''
        self.os_version = ''
        self.cpu_info = ''
        self.disk_info = ''
        self.memory_info = ''
        self.network_info = ''
        self.mount_info = ''
        self.dmesg_info = ''
        self.lldp_infos = []
        self._save_called = False

    def save(self):
        self._save_called = True


class TestCollectHostHardware(TestCase):
    """collect_host_hardware 测试类"""

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_hardware_success(self, mock_ssh_client):
        """测试采集硬件信息成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)

        # 模拟各命令的返回结果
        def execute_side_effect(cmd, *args, **kwargs):
            if 'uname -r' in cmd:
                return ("5.4.0--generic", "", 0)
            elif 'uptime' in cmd:
                return ("14:32:11 up 123 days", "", 0)
            elif 'os-release' in cmd:
                return ("NAME=\"Ubuntu\"\nVERSION=\"20.04\"", "", 0)
            elif 'lscpu' in cmd:
                return ("CPU: Intel(R) Xeon(R) CPU E5-2680", "", 0)
            elif 'lsblk' in cmd:
                return ("sda  100G", "", 0)
            elif '/meminfo' in cmd:
                return ("32768.45 GB", "", 0)
            elif 'ip addr' in cmd:
                return ("eth0  inet 192.168.1.100", "", 0)
            elif 'mount' in cmd:
                return ("/dev/sda1 on /", "", 0)
            elif 'dmesg -T' in cmd:
                return ("[Mon Jan 1 00:00:00 2020] boot", "", 0)
            return ("", "", 0)

        mock_instance.execute_command.side_effect = execute_side_effect

        host = MockHost()
        result = collect_host_hardware(host)

        self.assertEqual(result['arch_info'], '5.4.0--generic')
        self.assertEqual(result['uptime'], '14:32:11 up 123 days')
        self.assertEqual(result['os_version'], 'NAME="Ubuntu"\nVERSION="20.04"')
        self.assertEqual(result['cpu_info'], 'CPU: Intel(R) Xeon(R) CPU E5-2680')
        self.assertEqual(result['disk_info'], 'sda  100G')
        self.assertEqual(result['memory_info'], '32768.45 GB')
        self.assertEqual(result['network_info'], 'eth0  inet 192.168.1.100')
        self.assertEqual(result['mount_info'], '/dev/sda1 on /')
        self.assertEqual(result['dmesg_info'], '[Mon Jan 1 00:00:00 2020] boot')

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_hardware_partial_failure(self, mock_ssh_client):
        """测试部分命令失败的情况"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)

        def execute_side_effect(cmd, *args, **kwargs):
            if 'uname -r' in cmd:
                return ("5.4.0-generic", "", 0)
            elif 'lscpu' in cmd:
                return ("", "Command not found", 1)
            return ("", "", 0)

        mock_instance.execute_command.side_effect = execute_side_effect

        host = MockHost()
        result = collect_host_hardware(host)

        # uname 成功，其他失败时应该返回空字符串
        self.assertEqual(result['arch_info'], '5.4.0-generic')
        self.assertEqual(result['cpu_info'], '')

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_hardware_connection_failure(self, mock_ssh_client):
        """测试连接失败"""
        mock_ssh_client.side_effect = Exception("Connection refused")

        host = MockHost()
        result = collect_host_hardware(host)

        # 连接失败时返回空结果
        self.assertEqual(result['arch_info'], '')
        self.assertEqual(result['uptime'], '')
        self.assertEqual(result['os_version'], '')

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_hardware_empty_output(self, mock_ssh_client):
        """测试命令返回空结果"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.execute_command.return_value = ("", "", 0)

        host = MockHost()
        result = collect_host_hardware(host)

        self.assertEqual(result['arch_info'], '')
        self.assertEqual(result['uptime'], '')


class TestCollectHostLLDP(TestCase):
    """collect_host_lldp 测试类"""

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_lldp_success(self, mock_ssh_client):
        """测试采集 LLDP 信息成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)

        lldp_json = '''
        {
            "lldp": {
                "interface": [
                    {
                        "name": "eth0",
                        "chassis": {
                            "chassis": [
                                {"name": "switch01", "type": "mac", "id": {"value": "00:11:22:33:44:55"}}
                            ]
                        },
                        "port": {
                            "port": [
                                {"id": {"value": "eth1"}, "vlan": 100}
                            ]
                        }
                    },
                    {
                        "name": "eth1",
                        "chassis": {
                            "chassis": [
                                {"name": "router01", "type": "local", "id": {"value": "router-001"}}
                            ]
                        },
                        "port": {
                            "port": [
                                {"id": {"value": "ge-0/0/1"}, "vlan": 200}
                            ]
                        }
                    }
                ]
            }
        }
        '''
        mock_instance.execute_command.return_value = (lldp_json, "", 0)

        host = MockHost()
        result = collect_host_lldp(host)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ifname'], 'eth0')
        self.assertEqual(result[0]['peer_dev_name'], 'switch01')
        self.assertEqual(result[0]['peer_chassis_type'], 'mac')
        self.assertEqual(result[0]['peer_chassis_value'], '00:11:22:33:44:55')
        self.assertEqual(result[0]['peer_port_id'], 'eth1')
        self.assertEqual(result[0]['vlan'], '100')

        self.assertEqual(result[1]['ifname'], 'eth1')
        self.assertEqual(result[1]['peer_dev_name'], 'router01')
        self.assertEqual(result[1]['peer_chassis_type'], 'local')
        self.assertEqual(result[1]['peer_chassis_value'], 'router-001')
        self.assertEqual(result[1]['peer_port_id'], 'ge-0/0/1')
        self.assertEqual(result[1]['vlan'], '200')

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_lldp_empty(self, mock_ssh_client):
        """测试 lldpctl 返回空数据"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.execute_command.return_value = ("", "", 0)

        host = MockHost()
        result = collect_host_lldp(host)

        self.assertEqual(result, [])

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_lldp_command_failed(self, mock_ssh_client):
        """测试 lldpctl 命令失败"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.execute_command.return_value = ("", "lldpctl not found", 1)

        host = MockHost()
        result = collect_host_lldp(host)

        self.assertEqual(result, [])

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_lldp_connection_failure(self, mock_ssh_client):
        """测试连接失败"""
        mock_ssh_client.side_effect = Exception("Connection refused")

        host = MockHost()
        result = collect_host_lldp(host)

        self.assertEqual(result, [])

    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_lldp_invalid_json(self, mock_ssh_client):
        """测试返回无效 JSON"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.execute_command.return_value = ("not valid json", "", 0)

        host = MockHost()
        result = collect_host_lldp(host)

        self.assertEqual(result, [])


class TestUpdateHostHardwareInfo(TestCase):
    """update_host_hardware_info 测试类"""

    @patch('backend.utils.hardware_collector.collect_host_hardware')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_update_hardware_info_success(self, mock_ssh_client, mock_collect):
        """测试更新硬件信息成功"""
        mock_collect.return_value = {
            'arch_info': '5.4.0-generic',
            'uptime': '123 days',
            'os_version': 'Ubuntu 20.04',
            'cpu_info': 'Intel CPU',
            'disk_info': '100G',
            'memory_info': '32 GB',
            'network_info': 'eth0',
            'mount_info': '/dev/sda1',
            'dmesg_info': 'boot log',
        }

        host = MockHost()
        result = update_host_hardware_info(host)

        self.assertTrue(result)
        self.assertTrue(host._save_called)
        self.assertEqual(host.arch_info, '5.4.0-generic')
        self.assertEqual(host.uptime, '123 days')
        self.assertEqual(host.os_version, 'Ubuntu 20.04')
        self.assertEqual(host.cpu_info, 'Intel CPU')
        self.assertEqual(host.disk_info, '100G')
        self.assertEqual(host.memory_info, '32 GB')
        self.assertEqual(host.network_info, 'eth0')
        self.assertEqual(host.mount_info, '/dev/sda1')
        self.assertEqual(host.dmesg_info, 'boot log')

    @patch('backend.utils.hardware_collector.collect_host_hardware')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_update_hardware_info_failure(self, mock_ssh_client, mock_collect):
        """测试更新硬件信息失败"""
        mock_collect.side_effect = Exception("SSH connection failed")

        host = MockHost()
        result = update_host_hardware_info(host)

        self.assertFalse(result)


class TestUpdateHostLLDPInfo(TestCase):
    """update_host_lldp_info 测试类"""

    @patch('backend.utils.hardware_collector.collect_host_lldp')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_update_lldp_info_success(self, mock_ssh_client, mock_collect):
        """测试更新 LLDP 信息成功"""
        mock_collect.return_value = [
            {'ifname': 'eth0', 'peer_dev_name': 'switch01', 'peer_chassis_type': 'mac',
             'peer_chassis_value': '00:11:22:33:44:55', 'peer_port_id': 'eth1', 'vlan': '100'},
            {'ifname': 'eth1', 'peer_dev_name': 'router01', 'peer_chassis_type': 'local',
             'peer_chassis_value': 'router-001', 'peer_port_id': 'ge-0/0/1', 'vlan': '200'},
        ]

        host = MockHost()
        result = update_host_lldp_info(host)

        self.assertTrue(result)
        self.assertTrue(host._save_called)
        self.assertEqual(len(host.lldp_infos), 2)
        self.assertEqual(host.lldp_infos[0]['ifname'], 'eth0')
        self.assertEqual(host.lldp_infos[1]['vlan'], '200')

    @patch('backend.utils.hardware_collector.collect_host_lldp')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_update_lldp_info_failure(self, mock_ssh_client, mock_collect):
        """测试更新 LLDP 信息失败"""
        mock_collect.side_effect = Exception("SSH connection failed")

        host = MockHost()
        result = update_host_lldp_info(host)

        self.assertFalse(result)


class TestCollectAllHardwareInfo(TestCase):
    """collect_all_hardware_info 测试类"""

    @patch('backend.utils.hardware_collector.collect_host_lldp')
    @patch('backend.utils.hardware_collector.collect_host_hardware')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_all_success(self, mock_ssh_client, mock_collect_hw, mock_collect_lldp):
        """测试采集全部信息成功"""
        mock_collect_hw.return_value = {
            'arch_info': '5.4.0-generic',
            'uptime': '123 days',
            'os_version': 'Ubuntu 20.04',
            'cpu_info': 'Intel CPU',
            'disk_info': '100G',
            'memory_info': '32 GB',
            'network_info': 'eth0',
            'mount_info': '/dev/sda1',
            'dmesg_info': 'boot log',
        }
        mock_collect_lldp.return_value = [
            {'ifname': 'eth0', 'peer_dev_name': 'switch01'},
        ]

        host = MockHost()
        result = collect_all_hardware_info(host)

        self.assertIn('hardware', result)
        self.assertIn('lldp', result)
        self.assertEqual(result['hardware']['arch_info'], '5.4.0-generic')
        self.assertEqual(len(result['lldp']), 1)

    @patch('backend.utils.hardware_collector.collect_host_lldp')
    @patch('backend.utils.hardware_collector.collect_host_hardware')
    @patch('backend.utils.hardware_collector.SSHClient')
    def test_collect_all_partial_failure(self, mock_ssh_client, mock_collect_hw, mock_collect_lldp):
        """测试部分采集失败"""
        mock_collect_hw.side_effect = Exception("Hardware collect failed")
        mock_collect_lldp.return_value = [{'ifname': 'eth0'}]

        host = MockHost()
        # collect_all_hardware_info 没有异常处理，直接抛出
        with self.assertRaises(Exception) as context:
            collect_all_hardware_info(host)
        self.assertIn("Hardware collect failed", str(context.exception))