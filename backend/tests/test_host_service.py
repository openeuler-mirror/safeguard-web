"""
Host Service 单元测试
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from backend.models.host import Cluster, Host, VM
from backend.services.host import ClusterService, HostService, VMService
from backend.common.exceptions import (
    HostNotFoundError,
    VMNotFoundError,
    HardwareCollectError,
    LLDCollectError,
    PasswordUpdateError,
    VMOperationError,
)


class TestClusterService(TestCase):
    """ClusterService 测试类"""

    @classmethod
    def setUpTestData(cls):
        cls.cluster = Cluster.objects.create(
            name='TestCluster',
            description='Test Cluster Description'
        )

    def test_list_clusters(self):
        result = ClusterService.list_clusters()
        self.assertIn('total', result)
        self.assertIn('results', result)
        self.assertEqual(result['total'], 1)

    def test_list_clusters_pagination(self):
        result = ClusterService.list_clusters(page=1, page_size=5)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 5)

    def test_list_clusters_with_filters(self):
        result = ClusterService.list_clusters(filters={'name': 'TestCluster'})
        self.assertEqual(result['total'], 1)

    def test_get_cluster(self):
        cluster = ClusterService.get_cluster(self.cluster.id)
        self.assertIsNotNone(cluster)
        self.assertEqual(cluster.name, 'TestCluster')

    def test_get_cluster_not_found(self):
        cluster = ClusterService.get_cluster(9999)
        self.assertIsNone(cluster)

    def test_create_cluster(self):
        data = {'name': 'NewCluster', 'description': 'New Cluster'}
        cluster = ClusterService.create_cluster(data)
        self.assertEqual(cluster.name, 'NewCluster')

    def test_update_cluster(self):
        cluster = ClusterService.update_cluster(self.cluster.id, {'name': 'UpdatedCluster'})
        self.assertIsNotNone(cluster)
        self.assertEqual(cluster.name, 'UpdatedCluster')

    def test_update_cluster_not_found(self):
        cluster = ClusterService.update_cluster(9999, {'name': 'Updated'})
        self.assertIsNone(cluster)

    def test_delete_cluster(self):
        result = ClusterService.delete_cluster(self.cluster.id)
        self.assertTrue(result)
        self.assertIsNone(ClusterService.get_cluster(self.cluster.id))

    def test_delete_cluster_not_found(self):
        result = ClusterService.delete_cluster(9999)
        self.assertFalse(result)

    def test_get_cluster_topology(self):
        host = Host.objects.create(
            hostname='test-host', ip_address='192.168.1.100',
            port=22, username='root', password='password', cluster=self.cluster,
            lldp_infos=[{'ifname': 'eth0', 'peer_dev_name': 'switch01'}]
        )
        vm = VM.objects.create(
            name='test-vm', uuid='test-uuid-123', status='running',
            host=host, cluster=self.cluster
        )
        topology = ClusterService.get_cluster_topology(self.cluster.id)
        self.assertIsNotNone(topology)
        self.assertEqual(topology['cluster']['name'], 'TestCluster')
        self.assertEqual(len(topology['hosts']), 1)
        self.assertEqual(len(topology['vms']), 1)

    def test_get_cluster_topology_not_found(self):
        topology = ClusterService.get_cluster_topology(9999)
        self.assertIsNone(topology)


class TestHostService(TestCase):
    """HostService 测试类"""

    @classmethod
    def setUpTestData(cls):
        cls.cluster = Cluster.objects.create(name='TestCluster', description='Test')
        cls.host = Host.objects.create(
            hostname='test-host', ip_address='192.168.1.100',
            port=22, username='root', password='password', cluster=cls.cluster
        )

    def test_list_hosts(self):
        result = HostService.list_hosts()
        self.assertIn('total', result)
        self.assertEqual(result['total'], 1)

    def test_list_hosts_pagination(self):
        result = HostService.list_hosts(page=1, page_size=5)
        self.assertEqual(result['page'], 1)

    def test_get_host(self):
        host = HostService.get_host(self.host.id)
        self.assertIsNotNone(host)
        self.assertEqual(host.hostname, 'test-host')

    def test_get_host_not_found(self):
        host = HostService.get_host(9999)
        self.assertIsNone(host)

    def test_create_host(self):
        data = {
            'hostname': 'new-host', 'ip_address': '192.168.1.200',
            'port': 22, 'username': 'root', 'password': 'password'
        }
        host = HostService.create_host(data)
        self.assertEqual(host.hostname, 'new-host')

    def test_update_host(self):
        host = HostService.update_host(self.host.id, {'hostname': 'updated-host'})
        self.assertIsNotNone(host)
        self.assertEqual(host.hostname, 'updated-host')

    def test_delete_host(self):
        result = HostService.delete_host(self.host.id)
        self.assertTrue(result)

    def test_collect_hardware_host_not_found(self):
        with self.assertRaises(HostNotFoundError):
            HostService.collect_hardware(9999)

    @patch('backend.services.host.update_host_hardware_info')
    def test_collect_hardware_success(self, mock_update):
        mock_update.return_value = True
        self.host.arch_info = '5.4.0-generic'
        self.host.save()
        result = HostService.collect_hardware(self.host.id)
        self.assertEqual(result['arch_info'], '5.4.0-generic')

    @patch('backend.services.host.update_host_hardware_info')
    def test_collect_hardware_failure(self, mock_update):
        mock_update.return_value = False
        with self.assertRaises(HardwareCollectError):
            HostService.collect_hardware(self.host.id)

    def test_collect_lldp_host_not_found(self):
        with self.assertRaises(HostNotFoundError):
            HostService.collect_lldp(9999)

    @patch('backend.services.host.update_host_lldp_info')
    def test_collect_lldp_success(self, mock_update):
        mock_update.return_value = True
        self.host.lldp_infos = [{'ifname': 'eth0'}]
        self.host.save()
        result = HostService.collect_lldp(self.host.id)
        self.assertEqual(result, [{'ifname': 'eth0'}])

    @patch('backend.services.host.update_host_lldp_info')
    def test_collect_lldp_failure(self, mock_update):
        mock_update.return_value = False
        with self.assertRaises(LLDCollectError):
            HostService.collect_lldp(self.host.id)

    def test_collect_all_host_not_found(self):
        with self.assertRaises(HostNotFoundError):
            HostService.collect_all(9999)

    @patch('backend.services.host.update_host_lldp_info')
    @patch('backend.services.host.update_host_hardware_info')
    def test_collect_all_success(self, mock_hw, mock_lldp):
        mock_hw.return_value = True
        mock_lldp.return_value = True
        self.host.lldp_infos = [{'ifname': 'eth0'}]
        self.host.arch_info = '5.4.0-generic'
        self.host.save()
        result = HostService.collect_all(self.host.id)
        self.assertIn('hardware', result)
        self.assertIn('lldp', result)

    def test_generate_random_password(self):
        password = HostService.generate_random_password()
        self.assertEqual(len(password), 16)

    def test_generate_random_password_custom_length(self):
        password = HostService.generate_random_password(length=32)
        self.assertEqual(len(password), 32)

    def test_hash_password(self):
        hashed = HostService.hash_password('test_password')
        self.assertIsNotNone(hashed)
        self.assertNotEqual('test_password', hashed)

    def test_hash_password_consistency(self):
        hash1 = HostService.hash_password('test_password', 'key')
        hash2 = HostService.hash_password('test_password', 'key')
        self.assertEqual(hash1, hash2)

    def test_update_host_password_not_found(self):
        with self.assertRaises(HostNotFoundError):
            HostService.update_host_password(9999, 'new_password')

    def test_update_host_password_with_password(self):
        result = HostService.update_host_password(self.host.id, 'new_password')
        self.assertEqual(result, 'new_password')

    def test_update_host_password_auto_generate(self):
        result = HostService.update_host_password(self.host.id)
        self.assertEqual(len(result), 16)


class TestVMService(TestCase):
    """VMService 测试类"""

    @classmethod
    def setUpTestData(cls):
        cls.cluster = Cluster.objects.create(name='TestCluster', description='Test')
        cls.host = Host.objects.create(
            hostname='test-host', ip_address='192.168.1.100',
            port=22, username='root', password='password', cluster=cls.cluster
        )
        cls.vm = VM.objects.create(
            name='test-vm', uuid='test-uuid-123', status='stopped',
            host=cls.host, cluster=cls.cluster
        )

    def test_list_vms(self):
        result = VMService.list_vms()
        self.assertIn('total', result)
        self.assertEqual(result['total'], 1)

    def test_get_vm(self):
        vm = VMService.get_vm(self.vm.id)
        self.assertIsNotNone(vm)
        self.assertEqual(vm.name, 'test-vm')

    def test_get_vm_not_found(self):
        vm = VMService.get_vm(9999)
        self.assertIsNone(vm)

    def test_create_vm(self):
        data = {
            'name': 'new-vm', 'uuid': 'new-uuid-456',
            'status': 'stopped', 'host': self.host, 'cluster': self.cluster
        }
        vm = VMService.create_vm(data)
        self.assertEqual(vm.name, 'new-vm')

    def test_update_vm(self):
        vm = VMService.update_vm(self.vm.id, {'name': 'updated-vm'})
        self.assertIsNotNone(vm)
        self.assertEqual(vm.name, 'updated-vm')

    def test_delete_vm(self):
        result = VMService.delete_vm(self.vm.id)
        self.assertTrue(result)

    def test_start_vm_not_found(self):
        with self.assertRaises(VMNotFoundError):
            VMService.start_vm(9999)

    def test_start_vm(self):
        result = VMService.start_vm(self.vm.id)
        self.assertTrue(result.success)
        self.assertIn('成功', result.message)
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')
        self.assertEqual(result.new_status, 'running')

    def test_stop_vm(self):
        self.vm.status = 'running'
        self.vm.save()
        result = VMService.stop_vm(self.vm.id)
        self.assertTrue(result.success)
        self.assertIn('成功', result.message)
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'stopped')
        self.assertEqual(result.new_status, 'stopped')

    def test_reboot_vm(self):
        result = VMService.reboot_vm(self.vm.id)
        self.assertTrue(result.success)
        self.assertIn('成功', result.message)
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')
        self.assertEqual(result.new_status, 'running')

    def test_pause_vm(self):
        self.vm.status = 'running'
        self.vm.save()
        result = VMService.pause_vm(self.vm.id)
        self.assertTrue(result.success)
        self.assertIn('成功', result.message)
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'paused')
        self.assertEqual(result.new_status, 'paused')

    def test_resume_vm(self):
        self.vm.status = 'paused'
        self.vm.save()
        result = VMService.resume_vm(self.vm.id)
        self.assertTrue(result.success)
        self.assertIn('成功', result.message)
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')
        self.assertEqual(result.new_status, 'running')

    def test_get_vm_status_not_found(self):
        with self.assertRaises(VMNotFoundError):
            VMService.get_vm_status(9999)

    def test_get_vm_status(self):
        self.vm.status = 'running'
        self.vm.save()
        result = VMService.get_vm_status(self.vm.id)
        self.assertEqual(result, 'running')

    def test_delete_vm_from_libvirt_not_found(self):
        with self.assertRaises(VMNotFoundError):
            VMService.delete_vm_from_libvirt(9999)

    @patch('backend.utils.libvirt_client.LibvirtClient')
    def test_delete_vm_from_libvirt_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.stop_domain.return_value = (True, 'stopped')
        mock_client.undefine_domain.return_value = (True, 'undefined')
        mock_client._get_conn.return_value = MagicMock()
        mock_client_class.return_value = mock_client

        result = VMService.delete_vm_from_libvirt(self.vm.id)
        self.assertTrue(result.success)
        self.assertEqual(result.message, 'undefined')
        self.assertIsNone(result.vm)
        self.assertIsNone(result.new_status)

    @patch('backend.utils.libvirt_client.LibvirtClient')
    def test_create_vm_in_libvirt_not_found(self, mock_client_class):
        result = VMService.create_vm_in_libvirt(9999)
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'VM不存在')

    @patch('backend.utils.libvirt_client.LibvirtClient')
    def test_create_vm_in_libvirt_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client.create_domain.return_value = (True, 'created')
        mock_client_class.return_value = mock_client

        self.vm.vm_image_path = '/var/lib/libvirt/images/test.qcow2'
        self.vm.vm_network_bridge = 'mgmt'
        self.vm.save()

        result = VMService.create_vm_in_libvirt(self.vm.id)
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'created')
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')

    def test_generate_domain_xml(self):
        self.vm.vcpu = 4
        self.vm.memory = 8 * 1024**3  # 8 GiB
        self.vm.vm_image_path = '/var/lib/libvirt/images/test.qcow2'
        self.vm.vm_network_bridge = 'mgmt'
        self.vm.datadisk = [{'type': 'qcow2', 'path': '/var/lib/libvirt/images/data.qcow2'}]
        self.vm.save()

        xml = VMService._generate_domain_xml(self.vm)
        self.assertIn('<name>test-vm</name>', xml)
        self.assertIn('placement=\'static\'>4</vcpu>', xml)
        self.assertIn('<memory unit=\'GiB\'>8</memory>', xml)
        self.assertIn('test.qcow2', xml)
        self.assertIn('<source bridge=\'mgmt\'/>', xml)
        self.assertIn('data.qcow2', xml)