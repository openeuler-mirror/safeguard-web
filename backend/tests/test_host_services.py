from django.test import TestCase

from backend.models import Cluster, Host, VM
from backend.services.host import ClusterService, HostService, VMService


class ClusterServiceTest(TestCase):
    """ClusterService 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(
            name='TestCluster',
            description='测试集群'
        )

    def test_list_clusters(self):
        """测试获取集群列表"""
        result = ClusterService.list_clusters()
        self.assertEqual(result['total'], 1)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0].name, 'TestCluster')

    def test_list_clusters_with_pagination(self):
        """测试集群列表分页"""
        for i in range(15):
            Cluster.objects.create(name=f'Cluster{i}')
        result = ClusterService.list_clusters(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 5)

    def test_list_clusters_with_filter(self):
        """测试集群列表过滤"""
        Cluster.objects.create(name='FilterTest')
        result = ClusterService.list_clusters(filters={'name': 'FilterTest'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'FilterTest')

    def test_get_cluster(self):
        """测试获取集群详情"""
        cluster = ClusterService.get_cluster(self.cluster.id)
        self.assertIsNotNone(cluster)
        self.assertEqual(cluster.name, 'TestCluster')

    def test_get_cluster_not_found(self):
        """测试获取不存在的集群"""
        cluster = ClusterService.get_cluster(9999)
        self.assertIsNone(cluster)

    def test_create_cluster(self):
        """测试创建集群"""
        data = {'name': 'NewCluster', 'description': '新集群'}
        cluster = ClusterService.create_cluster(data)
        self.assertEqual(cluster.name, 'NewCluster')
        self.assertEqual(cluster.description, '新集群')

    def test_update_cluster(self):
        """测试更新集群"""
        data = {'name': 'UpdatedCluster', 'description': '更新后的描述'}
        cluster = ClusterService.update_cluster(self.cluster.id, data)
        self.assertEqual(cluster.name, 'UpdatedCluster')
        self.assertEqual(cluster.description, '更新后的描述')

    def test_update_cluster_not_found(self):
        """测试更新不存在的集群"""
        result = ClusterService.update_cluster(9999, {'name': 'Test'})
        self.assertIsNone(result)

    def test_delete_cluster(self):
        """测试删除集群"""
        result = ClusterService.delete_cluster(self.cluster.id)
        self.assertTrue(result)
        self.assertFalse(Cluster.objects.filter(id=self.cluster.id).exists())

    def test_delete_cluster_not_found(self):
        """测试删除不存在的集群"""
        result = ClusterService.delete_cluster(9999)
        self.assertFalse(result)


class HostServiceTest(TestCase):
    """HostService 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='TestCluster')
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            username='admin',
            password='secret',
            cluster=self.cluster,
            status='online'
        )

    def test_list_hosts(self):
        """测试获取主机列表"""
        result = HostService.list_hosts()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].hostname, 'test-host')

    def test_list_hosts_with_pagination(self):
        """测试主机列表分页"""
        for i in range(15):
            Host.objects.create(
                hostname=f'paginated-host{i}',
                ip_address=f'10.0.{i+1}.100',
                username='admin'
            )
        result = HostService.list_hosts(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_hosts_with_filter(self):
        """测试主机列表过滤"""
        result = HostService.list_hosts(filters={'hostname': 'test-host'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].hostname, 'test-host')

    def test_list_hosts_by_cluster(self):
        """测试按集群过滤主机"""
        result = HostService.list_hosts(filters={'cluster': self.cluster.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].hostname, 'test-host')

    def test_get_host(self):
        """测试获取主机详情"""
        host = HostService.get_host(self.host.id)
        self.assertIsNotNone(host)
        self.assertEqual(host.hostname, 'test-host')
        # 验证 select_related
        self.assertEqual(host.cluster.name, 'TestCluster')

    def test_get_host_not_found(self):
        """测试获取不存在的主机"""
        host = HostService.get_host(9999)
        self.assertIsNone(host)

    def test_create_host(self):
        """测试创建主机"""
        data = {
            'hostname': 'new-host',
            'ip_address': '192.168.1.200',
            'username': 'admin',
            'password': 'secret',
            'cluster': self.cluster
        }
        host = HostService.create_host(data)
        self.assertEqual(host.hostname, 'new-host')
        self.assertEqual(host.ip_address, '192.168.1.200')

    def test_update_host(self):
        """测试更新主机"""
        data = {'hostname': 'updated-host', 'status': 'offline'}
        host = HostService.update_host(self.host.id, data)
        self.assertEqual(host.hostname, 'updated-host')
        self.assertEqual(host.status, 'offline')

    def test_update_host_not_found(self):
        """测试更新不存在的主机"""
        result = HostService.update_host(9999, {'hostname': 'Test'})
        self.assertIsNone(result)

    def test_delete_host(self):
        """测试删除主机"""
        result = HostService.delete_host(self.host.id)
        self.assertTrue(result)
        self.assertFalse(Host.objects.filter(id=self.host.id).exists())

    def test_delete_host_not_found(self):
        """测试删除不存在的主机"""
        result = HostService.delete_host(9999)
        self.assertFalse(result)


class VMServiceTest(TestCase):
    """VMService 测试"""

    def setUp(self):
        self.cluster = Cluster.objects.create(name='TestCluster')
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.50',
            username='admin',
            cluster=self.cluster
        )
        self.vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440000',
            host=self.host,
            cluster=self.cluster,
            status='running',
            vcpu=4,
            memory=8589934592
        )

    def test_list_vms(self):
        """测试获取VM列表"""
        result = VMService.list_vms()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'test-vm')

    def test_list_vms_with_pagination(self):
        """测试VM列表分页"""
        for i in range(15):
            VM.objects.create(
                name=f'vm{i}',
                uuid=f'uuid-{i}',
                host=self.host
            )
        result = VMService.list_vms(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_vms_with_filter(self):
        """测试VM列表过滤"""
        result = VMService.list_vms(filters={'name': 'test-vm'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'test-vm')

    def test_list_vms_by_status(self):
        """测试按状态过滤VM"""
        VM.objects.create(name='stopped-vm', uuid='uuid-stopped', host=self.host, status='stopped')
        result = VMService.list_vms(filters={'status': 'running'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].status, 'running')

    def test_list_vms_by_host(self):
        """测试按宿主机过滤VM"""
        result = VMService.list_vms(filters={'host': self.host.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'test-vm')

    def test_list_vms_by_cluster(self):
        """测试按集群过滤VM"""
        result = VMService.list_vms(filters={'cluster': self.cluster.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'test-vm')

    def test_get_vm(self):
        """测试获取VM详情"""
        vm = VMService.get_vm(self.vm.id)
        self.assertIsNotNone(vm)
        self.assertEqual(vm.name, 'test-vm')
        # 验证 select_related
        self.assertEqual(vm.host.hostname, 'test-host')
        self.assertEqual(vm.cluster.name, 'TestCluster')

    def test_get_vm_not_found(self):
        """测试获取不存在的VM"""
        vm = VMService.get_vm(9999)
        self.assertIsNone(vm)

    def test_create_vm(self):
        """测试创建VM"""
        data = {
            'name': 'new-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440001',
            'host': self.host,
            'cluster': self.cluster,
            'status': 'stopped',
            'vcpu': 2,
            'memory': 4294967296
        }
        vm = VMService.create_vm(data)
        self.assertEqual(vm.name, 'new-vm')
        self.assertEqual(vm.vcpu, 2)
        self.assertEqual(vm.memory, 4294967296)

    def test_update_vm(self):
        """测试更新VM"""
        data = {'name': 'updated-vm', 'status': 'stopped', 'vcpu': 8}
        vm = VMService.update_vm(self.vm.id, data)
        self.assertEqual(vm.name, 'updated-vm')
        self.assertEqual(vm.status, 'stopped')
        self.assertEqual(vm.vcpu, 8)

    def test_update_vm_not_found(self):
        """测试更新不存在的VM"""
        result = VMService.update_vm(9999, {'name': 'Test'})
        self.assertIsNone(result)

    def test_delete_vm(self):
        """测试删除VM"""
        result = VMService.delete_vm(self.vm.id)
        self.assertTrue(result)
        self.assertFalse(VM.objects.filter(id=self.vm.id).exists())

    def test_delete_vm_not_found(self):
        """测试删除不存在的VM"""
        result = VMService.delete_vm(9999)
        self.assertFalse(result)
