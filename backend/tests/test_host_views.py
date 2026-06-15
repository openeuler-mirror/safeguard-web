"""主机相关视图集测试"""
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Cluster, Host, VM, Users, Authority, UserAuthority


class ClusterViewSetTest(APITestCase):
    """ClusterViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        # 创建管理员角色
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        # 创建测试用户
        self.user = Users.objects.create(
            user='testuser',
            password='testpass123',
            nickname='测试用户'
        )
        # 绑定管理员角色
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_clusters(self):
        """测试列出集群"""
        Cluster.objects.create(name='Cluster1')
        Cluster.objects.create(name='Cluster2')
        response = self.client.get('/api/clusters/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_cluster(self):
        """测试创建集群"""
        data = {'name': 'NewCluster', 'description': '新集群'}
        response = self.client.post('/api/clusters/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'NewCluster')

    def test_retrieve_cluster(self):
        """测试获取单个集群"""
        cluster = Cluster.objects.create(name='TestCluster')
        response = self.client.get(f'/api/clusters/{cluster.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'TestCluster')

    def test_update_cluster(self):
        """测试更新集群"""
        cluster = Cluster.objects.create(name='OriginalCluster')
        data = {'name': 'UpdatedCluster', 'description': '更新描述'}
        response = self.client.put(f'/api/clusters/{cluster.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'UpdatedCluster')

    def test_partial_update_cluster(self):
        """测试部分更新集群"""
        cluster = Cluster.objects.create(name='OriginalCluster')
        data = {'description': '新描述'}
        response = self.client.patch(f'/api/clusters/{cluster.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['description'], '新描述')

    def test_delete_cluster(self):
        """测试删除集群"""
        cluster = Cluster.objects.create(name='DeleteCluster')
        response = self.client.delete(f'/api/clusters/{cluster.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(Cluster.objects.filter(pk=cluster.pk).exists())

    def test_delete_cluster_with_hosts_fails(self):
        """测试删除有关联主机的集群失败"""
        cluster = Cluster.objects.create(name='ClusterWithHosts')
        Host.objects.create(
            hostname='host1',
            ip_address='192.168.1.1',
            username='admin',
            cluster=cluster
        )
        response = self.client.delete(f'/api/clusters/{cluster.pk}/')
        self.assertNotEqual(response.data['errno'], 0)
        self.assertIn('主机', response.data['errmsg'])

    def test_get_cluster_hosts(self):
        """测试获取集群关联的主机列表"""
        cluster = Cluster.objects.create(name='TestCluster')
        Host.objects.create(
            hostname='host1',
            ip_address='192.168.1.1',
            username='admin',
            cluster=cluster
        )
        response = self.client.get(f'/api/clusters/{cluster.pk}/hosts/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['hostname'], 'host1')

    def test_get_cluster_tree(self):
        """测试获取集群树"""
        Cluster.objects.create(name='Cluster1')
        Cluster.objects.create(name='Cluster2')
        response = self.client.get('/api/clusters/tree/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['data'][0]['label'], 'Cluster1')


class HostViewSetTest(APITestCase):
    """HostViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        # 创建管理员角色
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        # 创建测试用户
        self.user = Users.objects.create(
            user='testuser2',
            password='testpass123',
            nickname='测试用户2'
        )
        # 绑定管理员角色
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.cluster = Cluster.objects.create(name='TestCluster')

    def test_list_hosts(self):
        """测试列出主机"""
        Host.objects.create(hostname='host1', ip_address='192.168.1.1', username='admin')
        Host.objects.create(hostname='host2', ip_address='192.168.1.2', username='admin')
        response = self.client.get('/api/hosts/')
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_host(self):
        """测试创建主机"""
        data = {
            'hostname': 'new-host',
            'ip_address': '192.168.1.50',
            'username': 'admin',
            'password': 'secret',
            'cluster': self.cluster.id,
            'status': 'online'
        }
        response = self.client.post('/api/hosts/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['hostname'], 'new-host')

    def test_retrieve_host(self):
        """测试获取单个主机"""
        host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.60',
            username='admin'
        )
        response = self.client.get(f'/api/hosts/{host.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['hostname'], 'test-host')

    def test_update_host(self):
        """测试更新主机"""
        host = Host.objects.create(
            hostname='original',
            ip_address='192.168.1.70',
            username='admin'
        )
        data = {
            'hostname': 'updated',
            'ip_address': '192.168.1.70',
            'port': 22,
            'username': 'admin',
            'status': 'offline'
        }
        response = self.client.put(f'/api/hosts/{host.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['hostname'], 'updated')

    def test_partial_update_host(self):
        """测试部分更新主机"""
        host = Host.objects.create(
            hostname='original',
            ip_address='192.168.1.80',
            username='admin'
        )
        data = {'status': 'offline'}
        response = self.client.patch(f'/api/hosts/{host.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['status'], 'offline')

    def test_delete_host(self):
        """测试删除主机"""
        host = Host.objects.create(
            hostname='to-delete',
            ip_address='192.168.1.90',
            username='admin'
        )
        response = self.client.delete(f'/api/hosts/{host.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(Host.objects.filter(pk=host.pk).exists())


class VMViewSetTest(APITestCase):
    """VMViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        # 创建管理员角色
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        # 创建测试用户
        self.user = Users.objects.create(
            user='testuser3',
            password='testpass123',
            nickname='测试用户3'
        )
        # 绑定管理员角色
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.cluster = Cluster.objects.create(name='TestCluster')
        self.host = Host.objects.create(
            hostname='vm-host',
            ip_address='192.168.1.50',
            username='admin'
        )

    def test_list_vms(self):
        """测试列出VM"""
        VM.objects.create(name='vm1', uuid='uuid-1', host=self.host)
        VM.objects.create(name='vm2', uuid='uuid-2', host=self.host)
        response = self.client.get('/api/vms/')
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_vm(self):
        """测试创建VM"""
        data = {
            'name': 'new-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440001',
            'host': self.host.id,
            'cluster': self.cluster.id,
            'status': 'stopped',
            'vcpu': 4,
            'memory': 8589934592
        }
        response = self.client.post('/api/vms/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'new-vm')

    def test_retrieve_vm(self):
        """测试获取单个VM"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440002',
            host=self.host
        )
        response = self.client.get(f'/api/vms/{vm.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'test-vm')

    def test_update_vm(self):
        """测试更新VM"""
        vm = VM.objects.create(
            name='original-vm',
            uuid='550e8400-e29b-41d4-a716-446655440003',
            host=self.host
        )
        data = {
            'name': 'updated-vm',
            'host': self.host.id,
            'status': 'running',
            'vcpu': 4
        }
        response = self.client.put(f'/api/vms/{vm.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'updated-vm')

    def test_partial_update_vm(self):
        """测试部分更新VM"""
        vm = VM.objects.create(
            name='original-vm',
            uuid='550e8400-e29b-41d4-a716-446655440004',
            host=self.host
        )
        data = {'status': 'running'}
        response = self.client.patch(f'/api/vms/{vm.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['status'], 'running')

    def test_delete_vm(self):
        """测试删除VM"""
        vm = VM.objects.create(
            name='to-delete',
            uuid='550e8400-e29b-41d4-a716-446655440005',
            host=self.host
        )
        response = self.client.delete(f'/api/vms/{vm.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(VM.objects.filter(pk=vm.pk).exists())

    def test_vm_start_action(self):
        """测试VM启动操作"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440006',
            host=self.host
        )
        response = self.client.post(f'/api/vms/{vm.pk}/start/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('模拟模式', response.data['errmsg'])

    def test_vm_stop_action(self):
        """测试VM停止操作"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440007',
            host=self.host
        )
        response = self.client.post(f'/api/vms/{vm.pk}/stop/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('模拟模式', response.data['errmsg'])

    def test_vm_reboot_action(self):
        """测试VM重启操作"""
        vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440008',
            host=self.host
        )
        response = self.client.post(f'/api/vms/{vm.pk}/reboot/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('模拟模式', response.data['errmsg'])


class HostPermissionDeniedTest(APITestCase):
    """测试非管理员用户无权访问主机资源"""

    def setUp(self):
        """创建普通用户（非管理员）"""
        # 创建普通用户角色
        self.normal_auth = Authority.objects.create(
            authority_id=890,
            authority_name='普通用户'
        )
        # 创建普通用户
        self.user = Users.objects.create(
            user='normaluser',
            password='testpass123',
            nickname='普通用户'
        )
        UserAuthority.objects.create(user=self.user, authority=self.normal_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_non_admin_cannot_list_clusters(self):
        """测试非管理员不能列出集群"""
        response = self.client.get('/api/clusters/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_create_host(self):
        """测试非管理员不能创建主机"""
        data = {
            'hostname': 'new-host',
            'ip_address': '192.168.1.50',
            'username': 'admin'
        }
        response = self.client.post('/api/hosts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_create_vm(self):
        """测试非管理员不能创建VM"""
        host = Host.objects.create(
            hostname='vm-host',
            ip_address='192.168.1.50',
            username='admin'
        )
        data = {
            'name': 'new-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440001',
            'host': host.id
        }
        response = self.client.post('/api/vms/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HostActionViewSetTest(APITestCase):
    """Host Action ViewSet 测试（采集硬件、LLDP、密码更新等）"""

    def setUp(self):
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='adminuser',
            password='testpass123',
            nickname='管理员'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.cluster = Cluster.objects.create(name='TestCluster')
        self.host = Host.objects.create(
            hostname='test-host',
            ip_address='192.168.1.100',
            port=22,
            username='root',
            password='password',
            cluster=self.cluster
        )

    def test_collect_hardware_success(self):
        """测试采集硬件信息成功"""
        response = self.client.post(f'/api/hosts/{self.host.pk}/collect_hardware/')
        self.assertEqual(response.data['errno'], 0)

    def test_collect_hardware_not_found(self):
        """测试采集不存在的主机硬件信息"""
        response = self.client.post('/api/hosts/9999/collect_hardware/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_collect_lldp_success(self):
        """测试采集LLDP信息成功"""
        response = self.client.post(f'/api/hosts/{self.host.pk}/collect_lldp/')
        self.assertEqual(response.data['errno'], 0)

    def test_collect_lldp_not_found(self):
        """测试采集不存在的主机LLDP信息"""
        response = self.client.post('/api/hosts/9999/collect_lldp/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_get_host_lldp_success(self):
        """测试获取主机已保存的 LLDP 信息"""
        self.host.lldp_infos = [
            {
                'ifname': 'eth0',
                'peer_dev_name': 'switch-01',
                'peer_chassis_type': 'network',
                'peer_chassis_value': '00:11:22:33:44:55',
                'peer_port_id': 'Gi0/1',
                'vlan': '100',
            }
        ]
        self.host.save()
        response = self.client.get(f'/api/hosts/{self.host.pk}/lldp/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['ifname'], 'eth0')
        self.assertEqual(response.data['data'][0]['peer_dev_name'], 'switch-01')

    def test_get_host_lldp_empty(self):
        """测试获取未保存 LLDP 信息的主机"""
        response = self.client.get(f'/api/hosts/{self.host.pk}/lldp/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data'], [])

    def test_get_host_lldp_not_found(self):
        """测试获取不存在主机的 LLDP 信息"""
        response = self.client.get('/api/hosts/9999/lldp/')
        self.assertNotEqual(response.data['errno'], 0)

    def test_collect_all_success(self):
        """测试采集全部信息成功"""
        response = self.client.post(f'/api/hosts/{self.host.pk}/collect_all/')
        self.assertEqual(response.data['errno'], 0)

    def test_update_password_success(self):
        """测试更新密码成功"""
        response = self.client.post(
            f'/api/hosts/{self.host.pk}/update_password/',
            {'password': 'new_password'},
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('password', response.data['data'])

    def test_update_password_auto_generate(self):
        """测试自动生成密码"""
        response = self.client.post(f'/api/hosts/{self.host.pk}/update_password/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('password', response.data['data'])

    def test_update_password_with_key(self):
        """测试使用自定义key更新密码"""
        response = self.client.post(
            f'/api/hosts/{self.host.pk}/update_password/',
            {'password': 'custom_password', 'key': 'custom_key'},
            format='json'
        )
        self.assertEqual(response.data['errno'], 0)


class VMActionViewSetTest(APITestCase):
    """VM Action ViewSet 测试（start/stop/reboot/pause/resume/status）"""

    def setUp(self):
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='adminuser2',
            password='testpass123',
            nickname='管理员2'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.cluster = Cluster.objects.create(name='TestCluster')
        self.host = Host.objects.create(
            hostname='vm-host',
            ip_address='192.168.1.50',
            username='admin'
        )
        self.vm = VM.objects.create(
            name='test-vm',
            uuid='550e8400-e29b-41d4-a716-446655440001',
            status='stopped',
            host=self.host
        )

    def test_vm_start(self):
        """测试启动VM"""
        response = self.client.post(f'/api/vms/{self.vm.pk}/start/')
        self.assertEqual(response.data['errno'], 0)

    def test_vm_stop(self):
        """测试停止VM"""
        response = self.client.post(f'/api/vms/{self.vm.pk}/stop/')
        self.assertEqual(response.data['errno'], 0)

    def test_vm_reboot(self):
        """测试重启VM"""
        response = self.client.post(f'/api/vms/{self.vm.pk}/reboot/')
        self.assertEqual(response.data['errno'], 0)

    def test_vm_pause(self):
        """测试暂停VM"""
        response = self.client.post(f'/api/vms/{self.vm.pk}/pause/')
        self.assertEqual(response.data['errno'], 0)

    def test_vm_resume(self):
        """测试恢复VM"""
        response = self.client.post(f'/api/vms/{self.vm.pk}/resume/')
        self.assertEqual(response.data['errno'], 0)

    def test_vm_status(self):
        """测试获取VM状态"""
        response = self.client.get(f'/api/vms/{self.vm.pk}/status/')
        self.assertEqual(response.data['errno'], 0)
        self.assertIn('status', response.data['data'])

    def test_vm_action_not_found(self):
        """测试操作不存在VM"""
        response = self.client.post('/api/vms/9999/start/')
        self.assertNotEqual(response.data['errno'], 0)
