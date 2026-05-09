from django.test import TestCase

from backend.models import Cluster, Host, VM
from backend.serializers.host import (
    ClusterSerializer, ClusterCreateSerializer, ClusterUpdateSerializer,
    HostSerializer, HostCreateSerializer, HostUpdateSerializer, HostListSerializer,
    VMSerializer, VMCreateSerializer, VMUpdateSerializer, VMListSerializer,
)


class ClusterSerializerTest(TestCase):
    """ClusterSerializer 测试"""

    def test_serialize_cluster(self):
        """测试集群序列化"""
        cluster = Cluster.objects.create(
            name='TestCluster',
            description='测试集群',
            vcenter_id='vc-001'
        )
        serializer = ClusterSerializer(cluster)
        data = serializer.data
        self.assertEqual(data['name'], 'TestCluster')
        self.assertEqual(data['description'], '测试集群')
        self.assertEqual(data['vcenter_id'], 'vc-001')
        self.assertEqual(data['host_count'], 0)

    def test_serialize_cluster_with_hosts(self):
        """测试带主机的集群序列化"""
        cluster = Cluster.objects.create(name='ClusterWithHosts')
        Host.objects.create(hostname='host1', ip_address='192.168.1.1', username='admin', cluster=cluster)
        Host.objects.create(hostname='host2', ip_address='192.168.1.2', username='admin', cluster=cluster)
        serializer = ClusterSerializer(cluster)
        self.assertEqual(serializer.data['host_count'], 2)


class ClusterCreateSerializerTest(TestCase):
    """ClusterCreateSerializer 测试"""

    def test_create_cluster(self):
        """测试创建集群"""
        data = {'name': 'NewCluster', 'description': '新集群', 'vcenter_id': 'vc-002'}
        serializer = ClusterCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        cluster = serializer.save()
        self.assertEqual(cluster.name, 'NewCluster')

    def test_create_cluster_minimal(self):
        """测试最小数据创建集群"""
        data = {'name': 'MinimalCluster'}
        serializer = ClusterCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class ClusterUpdateSerializerTest(TestCase):
    """ClusterUpdateSerializer 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='OriginalCluster')

    def test_update_cluster(self):
        """测试更新集群"""
        data = {'name': 'UpdatedCluster', 'description': '更新描述'}
        serializer = ClusterUpdateSerializer(self.cluster, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        cluster = serializer.save()
        self.assertEqual(cluster.name, 'UpdatedCluster')
        self.assertEqual(cluster.description, '更新描述')


class HostSerializerTest(TestCase):
    """HostSerializer 测试"""

    def test_serialize_host(self):
        """测试主机序列化"""
        cluster = Cluster.objects.create(name='TestCluster')
        host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='admin',
            password='secret',
            cluster=cluster,
            status='online',
            os_type='Ubuntu 22.04'
        )
        serializer = HostSerializer(host)
        data = serializer.data
        self.assertEqual(data['hostname'], 'test-host')
        self.assertEqual(data['ip_address'], '192.168.1.100')
        self.assertEqual(data['port'], 22)
        self.assertEqual(data['username'], 'admin')
        self.assertEqual(data['cluster_name'], 'TestCluster')
        self.assertEqual(data['status'], 'online')
        self.assertEqual(data['os_type'], 'Ubuntu 22.04')
        # 密码不应该在序列化中返回
        self.assertNotIn('password', data)

    def test_serialize_host_without_cluster(self):
        """测试无集群的主机序列化"""
        host = Host.objects.create(
            hostname='no-cluster',
            ip_address='192.168.1.200',
            username='admin'
        )
        serializer = HostSerializer(host)
        self.assertIsNone(serializer.data['cluster_name'])


class HostCreateSerializerTest(TestCase):
    """HostCreateSerializer 测试"""

    def test_create_host(self):
        """测试创建主机"""
        cluster = Cluster.objects.create(name='TestCluster')
        data = {
            'hostname': 'new-host',
            'ip_address': '192.168.1.50',
            'port': 22,
            'username': 'admin',
            'password': 'secret',
            'cluster': cluster.id,
            'status': 'online',
            'os_type': 'CentOS 7'
        }
        serializer = HostCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        host = serializer.save()
        self.assertEqual(host.hostname, 'new-host')
        self.assertEqual(host.ip_address, '192.168.1.50')

    def test_create_host_minimal(self):
        """测试最小数据创建主机"""
        data = {
            'hostname': 'minimal-host',
            'ip_address': '192.168.1.60',
            'username': 'admin'
        }
        serializer = HostCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class HostUpdateSerializerTest(TestCase):
    """HostUpdateSerializer 测试"""

    def setUp(self):
        self.host = Host.objects.create(
            hostname='original',
            ip_address='192.168.1.70',
            username='admin'
        )

    def test_update_host(self):
        """测试更新主机"""
        data = {'hostname': 'updated', 'status': 'offline'}
        serializer = HostUpdateSerializer(self.host, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        host = serializer.save()
        self.assertEqual(host.hostname, 'updated')
        self.assertEqual(host.status, 'offline')

    def test_update_host_password(self):
        """测试更新主机密码"""
        data = {'password': 'newsecret'}
        serializer = HostUpdateSerializer(self.host, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        host = serializer.save()
        self.assertEqual(host.password, 'newsecret')

    def test_update_host_without_password(self):
        """测试不更新密码时密码保持不变"""
        self.host.password = 'original_secret'
        self.host.save()
        data = {'hostname': 'updated_name'}
        serializer = HostUpdateSerializer(self.host, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        host = serializer.save()
        self.assertEqual(host.password, 'original_secret')


class HostListSerializerTest(TestCase):
    """HostListSerializer 测试"""

    def test_serialize_host_list(self):
        """测试主机列表序列化"""
        cluster = Cluster.objects.create(name='ListCluster')
        host = Host.objects.create(
            hostname='list-host',
            ip_address='192.168.1.80',
            username='admin',
            cluster=cluster
        )
        serializer = HostListSerializer(host)
        data = serializer.data
        self.assertEqual(data['hostname'], 'list-host')
        self.assertEqual(data['cluster_name'], 'ListCluster')
        # 列表序列化器不包含 username/password
        self.assertNotIn('username', data)
        self.assertNotIn('password', data)


class VMSerializerTest(TestCase):
    """VMSerializer 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='VMCluster')
        self.host = Host.objects.create(
            hostname='vm-host',
            ip_address='192.168.1.90',
            username='admin'
        )

    def test_serialize_vm(self):
        """测试VM序列化"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440000',
            host=self.host,
            cluster=self.cluster,
            status='running',
            vcpu=4,
            memory=8589934592,
            disk=128849018880,
            ip_address='192.168.1.100',
            mac_address='00:0c:29:12:34:56',
            os_type='Ubuntu 22.04'
        )
        serializer = VMSerializer(vm)
        data = serializer.data
        self.assertEqual(data['name'], 'test-vm')
        self.assertEqual(data['uuid'], '550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(data['host_name'], 'vm-host')
        self.assertEqual(data['cluster_name'], 'VMCluster')
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['vcpu'], 4)
        self.assertEqual(data['memory'], 8589934592)
        self.assertEqual(data['disk'], 128849018880)
        self.assertEqual(data['ip_address'], '192.168.1.100')
        self.assertEqual(data['mac_address'], '00:0c:29:12:34:56')
        self.assertEqual(data['os_type'], 'Ubuntu 22.04')

    def test_serialize_vm_without_cluster(self):
        """测试无集群的VM序列化"""
        vm = VM.objects.create(
            name='no-cluster-vm',
            uuid='550e8400-e29b-41d4-a716-446655440001',
            host=self.host
        )
        serializer = VMSerializer(vm)
        self.assertIsNone(serializer.data['cluster_name'])


class VMCreateSerializerTest(TestCase):
    """VMCreateSerializer 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='CreateTestCluster')
        self.host = Host.objects.create(
            hostname='create-test-host',
            ip_address='192.168.1.110',
            username='admin'
        )

    def test_create_vm(self):
        """测试创建VM"""
        data = {
            'name': 'new-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440002',
            'host': self.host.id,
            'cluster': self.cluster.id,
            'status': 'stopped',
            'vcpu': 2,
            'memory': 4294967296,
            'disk': 64424509440,
            'ip_address': '192.168.1.120',
            'mac_address': '00:0c:29:12:34:57',
            'os_type': 'CentOS 7'
        }
        serializer = VMCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        vm = serializer.save()
        self.assertEqual(vm.name, 'new-vm')
        self.assertEqual(vm.vcpu, 2)

    def test_create_vm_minimal(self):
        """测试最小数据创建VM"""
        data = {
            'name': 'minimal-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440003',
            'host': self.host.id
        }
        serializer = VMCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class VMUpdateSerializerTest(TestCase):
    """VMUpdateSerializer 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='UpdateTestCluster')
        self.host = Host.objects.create(
            hostname='update-test-host',
            ip_address='192.168.1.130',
            username='admin'
        )
        self.vm = VM.objects.create(
            name='original-vm',
            uuid='550e8400-e29b-41d4-a716-446655440004',
            host=self.host
        )

    def test_update_vm(self):
        """测试更新VM"""
        data = {'name': 'updated-vm', 'status': 'running', 'vcpu': 8}
        serializer = VMUpdateSerializer(self.vm, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        vm = serializer.save()
        self.assertEqual(vm.name, 'updated-vm')
        self.assertEqual(vm.status, 'running')
        self.assertEqual(vm.vcpu, 8)

    def test_update_vm_status(self):
        """测试更新VM状态"""
        data = {'status': 'paused'}
        serializer = VMUpdateSerializer(self.vm, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        vm = serializer.save()
        self.assertEqual(vm.status, 'paused')


class VMListSerializerTest(TestCase):
    """VMListSerializer 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='ListTestCluster')
        self.host = Host.objects.create(
            hostname='list-test-host',
            ip_address='192.168.1.140',
            username='admin',
            cluster=self.cluster
        )

    def test_serialize_vm_list(self):
        """测试VM列表序列化"""
        vm = VM.objects.create(
            name='list-vm',
            uuid='550e8400-e29b-41d4-a716-446655440005',
            host=self.host,
            cluster=self.cluster,
            status='running',
            vcpu=4,
            memory=8589934592,
            ip_address='192.168.1.150',
            os_type='Ubuntu 22.04'
        )
        serializer = VMListSerializer(vm)
        data = serializer.data
        self.assertEqual(data['name'], 'list-vm')
        self.assertEqual(data['host_name'], 'list-test-host')
        self.assertEqual(data['cluster_name'], 'ListTestCluster')
        self.assertEqual(data['status'], 'running')
        # 列表序列化器不包含 memory/disk/mac_address
        self.assertNotIn('memory', data)
        self.assertNotIn('disk', data)
        self.assertNotIn('mac_address', data)
