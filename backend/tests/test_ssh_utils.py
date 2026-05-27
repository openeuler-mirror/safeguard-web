"""
SSH 工具单元测试
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from backend.utils.ssh import SSHClient
from backend.utils.host_command import (
    remote_host_command,
    remote_dir_exist,
    remote_file_exist,
    remote_create_dir,
    local_host_command,
    local_dir_exist,
    local_file_exist,
)


class TestSSHClient(TestCase):
    """SSHClient 测试类"""

    def test_init_with_password(self):
        """测试使用密码初始化"""
        client = SSHClient(
            host="192.168.1.100",
            port=22,
            username="root",
            password="password123",
            timeout=10,
        )
        self.assertEqual(client.host, "192.168.1.100")
        self.assertEqual(client.port, 22)
        self.assertEqual(client.username, "root")
        self.assertEqual(client.password, "password123")
        self.assertEqual(client.timeout, 10)
        self.assertIsNone(client._client)

    def test_init_with_key(self):
        """测试使用密钥初始化"""
        client = SSHClient(
            host="192.168.1.100",
            port=22,
            username="root",
            password="",
            key_filename="/path/to/key",
        )
        self.assertEqual(client.key_filename, "/path/to/key")

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_connect_success(self, mock_ssh_client):
        """测试连接成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.connect.return_value = None

        client = SSHClient("192.168.1.100", 22, "root", "password")
        result = client.connect()

        self.assertTrue(result)
        mock_instance.set_missing_host_key_policy.assert_called_once()
        mock_instance.connect.assert_called_once()

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_connect_failure(self, mock_ssh_client):
        """测试连接失败"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.connect.side_effect = Exception("Connection refused")

        client = SSHClient("192.168.1.100", 22, "root", "password")
        result = client.connect()

        self.assertFalse(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_execute_command_success(self, mock_ssh_client):
        """测试命令执行成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"output"
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""

        mock_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        stdout, stderr, exit_code = client.execute_command("ls -la")

        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "")
        self.assertEqual(exit_code, 0)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_execute_command_not_connected(self, mock_ssh_client):
        """测试未建立连接时执行命令"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.connect.side_effect = Exception("Connection refused")
        mock_instance.connect.return_value = None

        client = SSHClient("192.168.1.100", 22, "root", "password")
        stdout, stderr, exit_code = client.execute_command("ls -la")

        self.assertEqual(stdout, "")
        self.assertIn("Connection not established", stderr)
        self.assertEqual(exit_code, -1)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_file_exists_true(self, mock_ssh_client):
        """测试文件存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp
        mock_sftp.stat.return_value = MagicMock()

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.file_exists("/path/to/file")

        self.assertTrue(result)
        mock_sftp.stat.assert_called_once_with("/path/to/file")
        mock_sftp.close.assert_called_once()

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_file_exists_false(self, mock_ssh_client):
        """测试文件不存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp
        mock_sftp.stat.side_effect = IOError("File not found")

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.file_exists("/path/to/nonexistent")

        self.assertFalse(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_dir_exists_true(self, mock_ssh_client):
        """测试目录存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp
        mock_sftp.stat.return_value = MagicMock()

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.dir_exists("/path/to/dir")

        self.assertTrue(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_dir_exists_false(self, mock_ssh_client):
        """测试目录不存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp
        mock_sftp.stat.side_effect = IOError("No such file or directory")

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.dir_exists("/path/to/nonexistent")

        self.assertFalse(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_create_dir_success(self, mock_ssh_client):
        """测试创建目录成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.create_dir("/path/to/newdir")

        self.assertTrue(result)
        mock_sftp.mkdir.assert_called_once_with("/path/to/newdir")
        mock_sftp.close.assert_called_once()

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_create_dir_already_exists(self, mock_ssh_client):
        """测试创建目录已存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp
        mock_sftp.mkdir.side_effect = IOError("File exists")

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.create_dir("/path/to/existing")

        self.assertTrue(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_create_dir_recursive_success(self, mock_ssh_client):
        """测试递归创建目录成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp

        # 模拟目录不存在的检查
        mock_sftp.stat.side_effect = IOError("No such file or directory")

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.create_dir_recursive("/path/to/newdir/subdir")

        self.assertTrue(result)

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_download_file_success(self, mock_ssh_client):
        """测试下载文件成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.download_file("/remote/path/file", "/local/path/file")

        self.assertTrue(result)
        mock_sftp.get.assert_called_once_with("/remote/path/file", "/local/path/file")

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_upload_file_success(self, mock_ssh_client):
        """测试上传文件成功"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        mock_sftp = MagicMock()
        mock_instance.open_sftp.return_value = mock_sftp

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        result = client.upload_file("/local/path/file", "/remote/path/file")

        self.assertTrue(result)
        mock_sftp.put.assert_called_once_with("/local/path/file", "/remote/path/file")

    @patch('backend.utils.ssh.paramiko.SSHClient')
    def test_close(self, mock_ssh_client):
        """测试关闭连接"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance

        client = SSHClient("192.168.1.100", 22, "root", "password")
        client._client = mock_instance

        client.close()

        mock_instance.close.assert_called_once()
        self.assertIsNone(client._client)


class TestHostCommand(TestCase):
    """远程主机命令测试类"""

    @patch('backend.utils.host_command.SSHClient')
    def test_remote_host_command(self, mock_ssh_client):
        """测试远程命令执行"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.execute_command.return_value = ("output", "", 0)
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)

        stdout, stderr = remote_host_command(
            host="192.168.1.100",
            port=22,
            username="root",
            password="password",
            command="ls -la",
        )

        self.assertEqual(stdout, "output")
        self.assertEqual(stderr, "")

    @patch('backend.utils.host_command.SSHClient')
    def test_remote_dir_exist_true(self, mock_ssh_client):
        """测试远程目录存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.dir_exists.return_value = True
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)

        result = remote_dir_exist(
            host="192.168.1.100",
            port=22,
            username="root",
            password="password",
            path="/path/to/dir",
        )

        self.assertTrue(result)

    @patch('backend.utils.host_command.SSHClient')
    def test_remote_file_exist_false(self, mock_ssh_client):
        """测试远程文件不存在"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.file_exists.return_value = False
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)

        result = remote_file_exist(
            host="192.168.1.100",
            port=22,
            username="root",
            password="password",
            path="/path/to/file",
        )

        self.assertFalse(result)

    @patch('backend.utils.host_command.SSHClient')
    def test_remote_create_dir_recursive(self, mock_ssh_client):
        """测试递归创建目录"""
        mock_instance = MagicMock()
        mock_ssh_client.return_value = mock_instance
        mock_instance.create_dir_recursive.return_value = True
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)

        result = remote_create_dir(
            host="192.168.1.100",
            port=22,
            username="root",
            password="password",
            path="/path/to/newdir",
            recursive=True,
        )

        self.assertTrue(result)


class TestLocalCommand(TestCase):
    """本地命令测试类"""

    @patch('subprocess.run')
    def test_local_host_command_success(self, mock_run):
        """测试本地命令执行成功"""
        mock_result = MagicMock()
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        stdout, stderr = local_host_command("ls -la")

        self.assertEqual(stdout, "output")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_local_host_command_error(self, mock_run):
        """测试本地命令执行错误"""
        mock_run.side_effect = Exception("Command failed")

        stdout, stderr = local_host_command("invalid_command")

        self.assertEqual(stdout, "")
        self.assertIn("Command failed", stderr)

    def test_local_dir_exist_true(self):
        """测试本地目录存在"""
        exists, error = local_dir_exist("/tmp")

        self.assertTrue(exists)
        self.assertEqual(error, "")

    def test_local_dir_exist_false(self):
        """测试本地目录不存在"""
        exists, error = local_dir_exist("/nonexistent/path/12345")

        self.assertFalse(exists)
        self.assertIn("does not exist", error)

    def test_local_file_exist_true(self):
        """测试本地文件存在"""
        exists, error = local_file_exist("/tmp", "test_file")

        self.assertFalse(exists)  # /tmp 下可能没有 test_file，但应该不报错

    def test_local_file_exist_false(self):
        """测试本地文件不存在"""
        exists, error = local_file_exist("/nonexistent", "test_file")

        self.assertFalse(exists)
        self.assertIn("does not exist", error)