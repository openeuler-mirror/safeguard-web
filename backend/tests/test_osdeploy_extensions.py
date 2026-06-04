"""OSdeploy 扩展功能测试（DHCP Relay / noVNC / DiskPartition / PackageConfig / DownloadStatic / Repo扩展）"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models.user import Users
from backend.models.authority import Authority, UserAuthority
from backend.services.osdeploy.dhcp_relay_service import DHCPRelayService
from backend.services.osdeploy.novnc_service import NoVNCService
from backend.services.osdeploy.disk_partition_service import DiskPartitionService
from backend.services.osdeploy.package_service import PackageService


class DHCPRelayServiceTest(TestCase):
    """DHCPRelayService 单元测试"""

    def _mock_ssh(self, connect_return=True, cmd_result=("", "", 0)):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = connect_return
        mock_ssh.execute_command.return_value = cmd_result
        return mock_ssh

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_configure_relay_success(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh()
        mock_ssh_cls.return_value = mock_ssh

        result = DHCPRelayService.configure_relay({
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "port": "22", "interface_name": "Vlanif100", "dhcp_relay_ip": "192.168.1.1"
        })
        self.assertEqual(result["status"], "success")

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_configure_relay_connection_fail(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=False)
        mock_ssh_cls.return_value = mock_ssh

        result = DHCPRelayService.configure_relay({
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100", "dhcp_relay_ip": "192.168.1.1"
        })
        self.assertEqual(result["status"], "failed")

    def test_configure_relay_missing_params(self):
        result = DHCPRelayService.configure_relay({"host": "10.0.0.1"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("缺少", result["message"])

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_display_relay(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(cmd_result=("DHCP Relay: 192.168.1.1", "", 0))
        mock_ssh_cls.return_value = mock_ssh

        result = DHCPRelayService.display_relay({
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100"
        })
        self.assertEqual(result["status"], "success")
        self.assertIn("192.168.1.1", result["output"])

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_undo_relay(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh()
        mock_ssh_cls.return_value = mock_ssh

        result = DHCPRelayService.undo_relay({
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100", "dhcp_relay_ip": "192.168.1.1"
        })
        self.assertEqual(result["status"], "success")


class NoVNCServiceTest(TestCase):
    """NoVNCService 单元测试"""

    @patch("backend.services.osdeploy.novnc_service.SSHClient")
    def test_install_novnc_online(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ("online", "", 0),          # ping check
            ("", "", 0),                # rpm -qa tigervnc-server
            ("", "", 0),                # yum install
            ("", "", 0),                # rpm -qa python3
            ("", "", 0),                # rpm -qa numpy
            ("", "", 0),                # rpm -qa expect
            ("", "", 0),                # tar
            ("", "", 0),                # mkdir
            ("", "", 0),                # cp generatePem
            ("", "", 0),                # expect generatePem
            (":1", "", 0),              # vncserver -list has :1
            ("", "", 0),                # novnc_proxy
            ("200", "", 0),             # curl check
            ("", "", 0),                # systemctl status firewalld
        ]
        mock_ssh_cls.return_value = mock_ssh

        result = NoVNCService.install_novnc({
            "host": "10.0.0.1", "username": "root", "password": "pass"
        })
        self.assertEqual(result["status"], "success")

    @patch("backend.services.osdeploy.novnc_service.SSHClient")
    def test_close_novnc(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ("inactive", "", 0),        # firewalld inactive
            ("", "", 0),                # kill novnc
            (":1", "", 0),              # vncserver -list
            ("", "", 0),                # vncserver -kill
        ]
        mock_ssh_cls.return_value = mock_ssh

        result = NoVNCService.close_novnc({
            "host": "10.0.0.1", "username": "root", "password": "pass"
        })
        self.assertEqual(result["status"], "success")

    def test_install_novnc_missing_params(self):
        result = NoVNCService.install_novnc({"host": "10.0.0.1"})
        self.assertEqual(result["status"], "failed")


class DiskPartitionServiceTest(TestCase):
    """DiskPartitionService 单元测试"""

    @patch("backend.services.osdeploy.disk_partition_service.SSHClient")
    def test_get_disk_info(self, mock_ssh_cls):
        disk_json = '{"blockdevices": [{"name": "sda", "size": "100G", "type": "disk", "model": "VMware Disk"}]}'
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = (disk_json, "", 0)
        mock_ssh_cls.return_value = mock_ssh

        result = DiskPartitionService.get_disk_info("10.0.0.1", 22, "root", "pass")
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["disks"]), 1)
        self.assertEqual(result["disks"][0]["name"], "sda")

    @patch("backend.services.osdeploy.disk_partition_service.SSHClient")
    def test_is_system_disk(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = ("/\n", "", 0)
        mock_ssh_cls.return_value = mock_ssh

        result = DiskPartitionService.is_system_disk("sda", "10.0.0.1", 22, "root", "pass")
        self.assertTrue(result)

    @patch("backend.services.osdeploy.disk_partition_service.SSHClient")
    def test_execute_partition_free_mode(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        # is_free_disk returns True (no mountpoints)
        mock_ssh.execute_command.side_effect = [
            ("", "", 0),                # is_free_disk: no mountpoints
            ("", "", 0),                # mklabel gpt
            ("", "", 0),                # mkpart
            ("", "", 0),                # mkfs.ext4
            ("", "", 0),                # mkdir
            ("", "", 0),                # mount
            ("", "", 0),                # fstab
        ]
        mock_ssh_cls.return_value = mock_ssh

        result = DiskPartitionService.execute_partition(
            "sdb", "Free", {"partitions": [{"size": "50G", "fstype": "ext4", "mountpoint": "/data"}]},
            "10.0.0.1", 22, "root", "pass"
        )
        self.assertEqual(result["status"], "success")


class PackageServiceTest(TestCase):
    """PackageService 单元测试"""

    def test_generate_spec_success(self):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.spec")
            result = PackageService.generate_spec({
                "package_name": "myapp",
                "version": "2.0.0",
                "output_path": output_path,
            })
            self.assertEqual(result["status"], "success")
            self.assertTrue(os.path.exists(output_path))
            self.assertIn("Name:           myapp", result["content"])
            self.assertIn("Version:        2.0.0", result["content"])

    def test_generate_spec_default(self):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "oskit.spec")
            result = PackageService.generate_spec({"output_path": output_path})
            self.assertEqual(result["status"], "success")
            self.assertTrue(os.path.exists(output_path))


class OSdeployExtensionsViewSetTest(APITestCase):
    """OSdeploy 扩展功能 API 集成测试"""

    def setUp(self):
        self.user = Users.objects.create(
            user="ext_test", nickname="Ext Test", email="ext@test.com", enable=1
        )
        self.user.set_password("testpass")
        self.user.save()
        self.admin_auth = Authority.objects.create(authority_id=888, authority_name="超级管理员")
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_dhcp_relay_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = ("", "", 0)
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/pxe-servers/relay/", {
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100", "dhcp_relay_ip": "192.168.1.1"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_dhcp_relay_display_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = ("Relay: 192.168.1.1", "", 0)
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/pxe-servers/relay-display/", {
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.osdeploy.dhcp_relay_service.SSHClient")
    def test_dhcp_relay_undo_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = ("", "", 0)
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/pxe-servers/relay-undo/", {
            "host": "10.0.0.1", "username": "admin", "password": "pass",
            "interface_name": "Vlanif100", "dhcp_relay_ip": "192.168.1.1"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    def test_download_static_api(self):
        response = self.client.post("/api/autoinstall/download-static/", {
            "iso": "culinux_x86"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    def test_download_static_invalid(self):
        response = self.client.post("/api/autoinstall/download-static/", {
            "iso": "invalid"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 1001)

    @patch("backend.services.osdeploy.novnc_service.SSHClient")
    def test_novnc_install_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ("online", "", 0),
            ("tigervnc-server-1.0", "", 0),
            ("python3-3.9", "", 0),
            ("numpy-1.0", "", 0),
            ("expect-5.45", "", 0),
            ("", "", 0), ("", "", 0), ("", "", 0), ("", "", 0),
            (":1", "", 0), ("", "", 0),
            ("200", "", 0), ("", "", 0),
        ]
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/novnc/install/", {
            "host": "10.0.0.1", "username": "root", "password": "pass"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.osdeploy.novnc_service.SSHClient")
    def test_novnc_close_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ("inactive", "", 0), ("", "", 0),
            (":1", "", 0), ("", "", 0),
        ]
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/novnc/close/", {
            "host": "10.0.0.1", "username": "root", "password": "pass"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    @patch("backend.services.osdeploy.disk_partition_service.SSHClient")
    def test_disk_partition_info_api(self, mock_ssh_cls):
        disk_json = '{"blockdevices": [{"name": "sda", "size": "100G", "type": "disk", "model": "VMware"}]}'
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = (disk_json, "", 0)
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/disk-partition/info/", {
            "host": "10.0.0.1", "username": "root", "password": "pass"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    def test_package_config_api(self):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.spec")
            response = self.client.post("/api/packages/config/", {
                "package_name": "myapp",
                "version": "1.0.0",
                "output_path": output_path,
            }, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["errno"], 0)
            self.assertIn("path", response.data["data"])