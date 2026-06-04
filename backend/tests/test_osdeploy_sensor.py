"""Sensor 部署服务及视图测试"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models.user import Users
from backend.models.authority import Authority, UserAuthority
from backend.services.osdeploy.sensor_service import SensorService


class SensorServiceTest(TestCase):
    """SensorService 单元测试"""

    def _mock_ssh(self, connect_return=True, cmd_results=None):
        """辅助方法：构造 mock SSHClient"""
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = connect_return
        if cmd_results is None:
            cmd_results = []
        mock_ssh.execute_command.side_effect = cmd_results
        return mock_ssh

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_install_sensor_success(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=True, cmd_results=[
            ('PRETTY_NAME="CentOS Linux 7"\nVERSION_ID="7"', '', 0),   # cat /etc/os-release
            ('x86_64', '', 0),                          # uname -m
            ('/opt/sensor/rpms/sensor-1.0.0-1.el7.x86_64.rpm', '', 0),  # find rpm
            ('Installed successfully', '', 0),           # yum install
        ])
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.install_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
            "port": "22",
            "base_path": "/opt/sensor/rpms",
        })
        self.assertEqual(result["status"], "success")
        self.assertIn("job_id", result)

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_install_sensor_connection_fail(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=False)
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.install_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
        })
        self.assertEqual(result["status"], "failed")
        self.assertIn("无法连接", result["message"])

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_install_sensor_unsupported_os(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=True, cmd_results=[
            ('PRETTY_NAME="Ubuntu 22.04"', '', 0),
        ])
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.install_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
        })
        self.assertEqual(result["status"], "failed")
        self.assertIn("不支持", result["message"])

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_operate_sensor_start(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=True, cmd_results=[
            ('', '', 0),  # systemctl start sensor
        ])
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.operate_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
            "port": "22",
        }, "start")
        self.assertEqual(result["status"], "success")

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_operate_sensor_delete(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=True, cmd_results=[
            ('', '', 0),
        ])
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.operate_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
        }, "delete")
        self.assertEqual(result["status"], "success")

    def test_operate_sensor_invalid(self):
        result = SensorService.operate_sensor({
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
        }, "invalid")
        self.assertEqual(result["status"], "failed")
        self.assertIn("无效操作", result["message"])

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_update_config_success(self, mock_ssh_cls):
        mock_ssh = self._mock_ssh(connect_return=True, cmd_results=[
            ('[common]\nroot_log_path = "/var/log/sensor"\n', '', 0),  # cat config
            ('', '', 0),  # write config
            ('', '', 0),  # restart
        ])
        mock_ssh_cls.return_value = mock_ssh

        result = SensorService.update_config(
            "SN123",
            {"common": {"root_log_path": "/opt/logs"}},
            {"host": "10.0.0.1", "username": "root", "password": "pass"},
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("config", result)

    def test_merge_configs(self):
        base = {"a": 1, "b": {"c": 2, "d": 3}}
        override = {"b": {"c": 99}}
        merged = SensorService._merge_configs(base, override)
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["c"], 99)
        self.assertEqual(merged["b"]["d"], 3)


class SensorViewSetTest(APITestCase):
    """SensorViewSet API 集成测试"""

    def setUp(self):
        self.user = Users.objects.create(
            user="sensor_test",
            nickname="Sensor Test",
            email="sensor@test.com",
            enable=1,
        )
        self.user.set_password("testpass")
        self.user.save()
        self.admin_auth = Authority.objects.create(authority_id=888, authority_name="超级管理员")
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_install_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ('PRETTY_NAME="CentOS Linux 7"\nVERSION_ID="7"', '', 0),
            ('x86_64', '', 0),
            ('/opt/sensor/rpms/sensor-1.0.0-1.el7.x86_64.rpm', '', 0),
            ('Installed', '', 0),
        ]
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/sensors/install/", {
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)
        self.assertIn("job_id", response.data["data"])

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_operate_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.return_value = ("", "", 0)
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/sensors/operate/", {
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
            "operate": "stop",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)

    def test_operate_api_invalid(self):
        response = self.client.post("/api/sensors/operate/", {
            "host": "10.0.0.1",
            "username": "root",
            "password": "pass",
            "operate": "invalid",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 7201)

    @patch("backend.services.osdeploy.sensor_service.SSHClient")
    def test_update_config_api(self, mock_ssh_cls):
        mock_ssh = MagicMock()
        mock_ssh.connect.return_value = True
        mock_ssh.execute_command.side_effect = [
            ('[grpc]\nserver_ip = "0.0.0.0"\n', '', 0),
            ('', '', 0),
            ('', '', 0),
        ]
        mock_ssh_cls.return_value = mock_ssh

        response = self.client.post("/api/sensors/update-config/", {
            "serial_number": "SN123",
            "host_info": {
                "host": "10.0.0.1",
                "username": "root",
                "password": "pass",
            },
            "config": {
                "grpc": {"server_ip": "127.0.0.1"},
            },
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["errno"], 0)
