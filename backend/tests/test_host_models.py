from django.test import TestCase

from backend.models import Cluster, Host, VM, Image


class ClusterModelTest(TestCase):
    """Cluster 模型测试"""

    def test_create_cluster(self):
        """测试创建集群"""
        cluster = Cluster.objects.create(
            name='TestCluster',
            description='测试集群',
            vcenter_id='vc-001'
        )
        self.assertEqual(cluster.name, 'TestCluster')
        self.assertEqual(cluster.description, '测试集群')
        self.assertEqual(cluster.vcenter_id, 'vc-001')

    def test_cluster_name_unique(self):
        """测试集群名称唯一性"""
        Cluster.objects.create(name='UniqueCluster')
        with self.assertRaises(Exception):
            Cluster.objects.create(name='UniqueCluster')

    def test_cluster_str(self):
        """测试集群字符串表示"""
        cluster = Cluster(name='MyCluster')
        self.assertEqual(str(cluster), 'MyCluster')

    def test_cluster_default_values(self):
        """测试集群默认值"""
        cluster = Cluster.objects.create(name='DefaultCluster')
        self.assertEqual(cluster.description, '')
        self.assertEqual(cluster.vcenter_id, '')


class HostModelTest(TestCase):
    """Host 模型测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='TestCluster')

    def test_create_host(self):
        """测试创建主机"""
        host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='admin',
            password='secret',
            cluster=self.cluster,
            status='online',
            os_type='Ubuntu 22.04'
        )
        self.assertEqual(host.hostname, 'test-host')
        self.assertEqual(host.ip_address, '192.168.1.100')
        self.assertEqual(host.port, 22)
        self.assertEqual(host.username, 'admin')
        self.assertEqual(host.status, 'online')
        self.assertEqual(host.os_type, 'Ubuntu 22.04')
        self.assertEqual(host.cluster, self.cluster)

    def test_host_str(self):
        """测试主机字符串表示"""
        host = Host(hostname='my-host', ip_address='192.168.1.1')
        self.assertEqual(str(host), 'my-host (192.168.1.1)')

    def test_host_ip_unique(self):
        """测试主机IP唯一性"""
        Host.objects.create(hostname='host1', ip_address='192.168.1.1', username='root')
        with self.assertRaises(Exception):
            Host.objects.create(hostname='host2', ip_address='192.168.1.1', username='root')

    def test_host_default_port(self):
        """测试主机默认端口"""
        host = Host.objects.create(
            hostname='default-port',
            ip_address='192.168.1.2',
            username='root'
        )
        self.assertEqual(host.port, 22)

    def test_host_default_status(self):
        """测试主机默认状态"""
        host = Host.objects.create(
            hostname='status-test',
            ip_address='192.168.1.3',
            username='root'
        )
        self.assertEqual(host.status, 'offline')

    def test_host_cluster_relation(self):
        """测试主机与集群的关系"""
        host1 = Host.objects.create(
            hostname='host1',
            ip_address='192.168.1.10',
            username='root',
            cluster=self.cluster
        )
        host2 = Host.objects.create(
            hostname='host2',
            ip_address='192.168.1.11',
            username='root',
            cluster=self.cluster
        )
        self.assertEqual(self.cluster.host_set.count(), 2)
        self.assertIn(host1, self.cluster.host_set.all())
        self.assertIn(host2, self.cluster.host_set.all())

    def test_host_without_cluster(self):
        """测试无集群关联的主机"""
        host = Host.objects.create(
            hostname='no-cluster',
            ip_address='192.168.1.200',
            username='root'
        )
        self.assertIsNone(host.cluster)


class VMModelTest(TestCase):
    """VM 模型测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='VMCluster')
        self.host = Host.objects.create(
            hostname='vm-host',
            ip_address='192.168.1.50',
            username='root',
            cluster=self.cluster
        )

    def test_create_vm(self):
        """测试创建VM"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440000',
            host=self.host,
            cluster=self.cluster,
            status='running',
            vcpu=4,
            memory=8589934592,  # 8GB
            disk=128849018880,  # 120GB
            ip_address='192.168.1.100',
            mac_address='00:0c:29:12:34:56',
            os_type='Ubuntu 22.04'
        )
        self.assertEqual(vm.name, 'test-vm')
        self.assertEqual(vm.uuid, '550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(vm.host, self.host)
        self.assertEqual(vm.cluster, self.cluster)
        self.assertEqual(vm.status, 'running')
        self.assertEqual(vm.vcpu, 4)
        self.assertEqual(vm.memory, 8589934592)
        self.assertEqual(vm.disk, 128849018880)
        self.assertEqual(vm.ip_address, '192.168.1.100')
        self.assertEqual(vm.mac_address, '00:0c:29:12:34:56')
        self.assertEqual(vm.os_type, 'Ubuntu 22.04')

    def test_vm_str(self):
        """测试VM字符串表示"""
        vm = VM(name='my-vm', ip_address='192.168.1.1')
        self.assertEqual(str(vm), 'my-vm (192.168.1.1)')

    def test_vm_str_no_ip(self):
        """测试无IP的VM字符串表示"""
        vm = VM(name='no-ip-vm', ip_address=None)
        self.assertEqual(str(vm), 'no-ip-vm (No IP)')

    def test_vm_uuid_unique(self):
        """测试VM UUID唯一性"""
        VM.objects.create(
            name='vm1',
            uuid='unique-uuid-001',
            host=self.host
        )
        with self.assertRaises(Exception):
            VM.objects.create(
                name='vm2',
                uuid='unique-uuid-001',
                host=self.host
            )

    def test_vm_default_status(self):
        """测试VM默认状态"""
        vm = VM.objects.create(
            name='default-status',
            uuid='uuid-default',
            host=self.host
        )
        self.assertEqual(vm.status, 'stopped')

    def test_vm_default_vcpu(self):
        """测试VM默认CPU核数"""
        vm = VM.objects.create(
            name='default-cpu',
            uuid='uuid-cpu',
            host=self.host
        )
        self.assertEqual(vm.vcpu, 1)

    def test_vm_host_relation(self):
        """测试VM与宿主机的关系"""
        vm1 = VM.objects.create(name='vm1', uuid='uuid-vm1', host=self.host)
        vm2 = VM.objects.create(name='vm2', uuid='uuid-vm2', host=self.host)
        self.assertEqual(self.host.vms.count(), 2)
        self.assertIn(vm1, self.host.vms.all())
        self.assertIn(vm2, self.host.vms.all())

    def test_vm_cluster_relation(self):
        """测试VM与集群的关系"""
        vm = VM.objects.create(
            name='clustered-vm',
            uuid='uuid-cluster',
            host=self.host,
            cluster=self.cluster
        )
        self.assertEqual(vm.cluster, self.cluster)

    def test_vm_without_cluster(self):
        """测试无集群关联的VM"""
        vm = VM.objects.create(
            name='no-cluster-vm',
            uuid='uuid-no-cluster',
            host=self.host
        )
        self.assertIsNone(vm.cluster)

    def test_vm_status_choices(self):
        """测试VM状态选项"""
        for status_value, status_label in VM.STATUS_CHOICES:
            vm = VM.objects.create(
                name=f'vm-{status_value}',
                uuid=f'uuid-{status_value}',
                host=self.host,
                status=status_value
            )
            self.assertEqual(vm.status, status_value)

    def test_vm_cascade_delete(self):
        """测试删除宿主机时VM也被删除"""
        vm = VM.objects.create(
            name='cascade-vm',
            uuid='uuid-cascade',
            host=self.host
        )
        vm_id = vm.id
        self.host.delete()
        self.assertFalse(VM.objects.filter(id=vm_id).exists())

    def test_vm_extended_fields(self):
        """测试VM扩展字段"""
        vm = VM.objects.create(
            name='extended-vm',
            uuid='uuid-extended',
            host=self.host,
            imageid='img-001',
            sysdisk={'type': 'qcow2', 'size': '100G'},
            datadisk=[{'type': 'qcow2', 'path': '/data/disk.qcow2'}],
            status_message='VM is running normally',
            vm_image_path='/var/lib/libvirt/images/extended.qcow2',
            vm_disk_path='/var/lib/libvirt/images/extended-disk.qcow2',
            vm_network_bridge='mgmt'
        )
        self.assertEqual(vm.imageid, 'img-001')
        self.assertEqual(vm.sysdisk, {'type': 'qcow2', 'size': '100G'})
        self.assertEqual(vm.datadisk, [{'type': 'qcow2', 'path': '/data/disk.qcow2'}])
        self.assertEqual(vm.status_message, 'VM is running normally')
        self.assertEqual(vm.vm_image_path, '/var/lib/libvirt/images/extended.qcow2')
        self.assertEqual(vm.vm_disk_path, '/var/lib/libvirt/images/extended-disk.qcow2')
        self.assertEqual(vm.vm_network_bridge, 'mgmt')

    def test_vm_default_extended_fields(self):
        """测试VM扩展字段默认值"""
        vm = VM.objects.create(
            name='default-extended',
            uuid='uuid-default-extended',
            host=self.host
        )
        self.assertEqual(vm.imageid, '')
        self.assertEqual(vm.sysdisk, {})
        self.assertEqual(vm.datadisk, [])
        self.assertEqual(vm.status_message, '')


class ImageModelTest(TestCase):
    """Image 模型测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='ImageCluster')
        self.host = Host.objects.create(
            hostname='image-host',
            ip_address='192.168.1.60',
            username='root',
            cluster=self.cluster
        )

    def test_create_image(self):
        """测试创建镜像"""
        image = Image.objects.create(
            id='img-001',
            name='centos7.qcow2',
            ostype='centos',
            path='/var/lib/libvirt/images/centos7.qcow2',
            host=self.host
        )
        self.assertEqual(image.id, 'img-001')
        self.assertEqual(image.name, 'centos7.qcow2')
        self.assertEqual(image.ostype, 'centos')
        self.assertEqual(image.path, '/var/lib/libvirt/images/centos7.qcow2')
        self.assertEqual(image.host, self.host)

    def test_image_str(self):
        """测试镜像字符串表示"""
        image = Image(id='img-test', name='test-image', ostype='ubuntu')
        self.assertEqual(str(image), 'test-image (ubuntu)')

    def test_image_host_relation(self):
        """测试镜像与宿主机的关系"""
        image = Image.objects.create(
            id='img-host-relation',
            name='relation-test',
            path='/test/path',
            host=self.host
        )
        self.assertEqual(image.host, self.host)
        self.assertIn(image, self.host.image_set.all())

    def test_image_cascade_delete(self):
        """测试删除宿主机时镜像也被删除"""
        image = Image.objects.create(
            id='img-cascade',
            name='cascade-test',
            path='/test/path',
            host=self.host
        )
        image_id = image.id
        self.host.delete()
        self.assertFalse(Image.objects.filter(id=image_id).exists())
