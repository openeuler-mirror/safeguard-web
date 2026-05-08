"""Host 相关 Pydantic Schema 测试"""
from django.test import TestCase

from backend.schemas.host import (
    ClusterBase, ClusterCreateRequest, ClusterUpdateRequest, ClusterResponse,
    HostBase, HostCreateRequest, HostUpdateRequest, HostResponse,
    VMBase, VMCreateRequest, VMUpdateRequest, VMResponse,
)


class ClusterSchemaTest(TestCase):
    """Cluster Schema 测试"""

    def test_cluster_base_valid(self):
        """测试有效的集群基础模型"""
        data = {'name': 'TestCluster', 'description': '测试', 'vcenter_id': 'vc-001'}
        schema = ClusterBase(**data)
        self.assertEqual(schema.name, 'TestCluster')
        self.assertEqual(schema.description, '测试')
        self.assertEqual(schema.vcenter_id, 'vc-001')

    def test_cluster_base_minimal(self):
        """测试最小集群数据"""
        schema = ClusterBase(name='MinimalCluster')
        self.assertEqual(schema.name, 'MinimalCluster')
        self.assertEqual(schema.description, '')
        self.assertEqual(schema.vcenter_id, '')

    def test_cluster_create_request(self):
        """测试创建集群请求"""
        data = {'name': 'NewCluster'}
        schema = ClusterCreateRequest(**data)
        self.assertEqual(schema.name, 'NewCluster')

    def test_cluster_update_request(self):
        """测试更新集群请求"""
        data = {'name': 'UpdatedCluster', 'description': '更新描述'}
        schema = ClusterUpdateRequest(**data)
        self.assertEqual(schema.name, 'UpdatedCluster')
        self.assertEqual(schema.description, '更新描述')

    def test_cluster_name_required(self):
        """测试集群名称为必填"""
        with self.assertRaises(Exception):
            ClusterBase()

    def test_cluster_response(self):
        """测试集群响应模型"""
        data = {
            'id': 1,
            'name': 'ResponseCluster',
            'description': '响应描述',
            'vcenter_id': 'vc-002',
            'host_count': 5,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = ClusterResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.host_count, 5)


class HostSchemaTest(TestCase):
    """Host Schema 测试"""

    def test_host_base_valid(self):
        """测试有效的主机基础模型"""
        data = {
            'hostname': 'test-host',
            'ip_address': '192.168.1.100',
            'port': 22,
            'username': 'admin',
            'password': 'secret',
            'cluster': 1,
            'status': 'online',
            'os_type': 'Ubuntu 22.04'
        }
        schema = HostBase(**data)
        self.assertEqual(schema.hostname, 'test-host')
        self.assertEqual(schema.ip_address, '192.168.1.100')
        self.assertEqual(schema.status, 'online')

    def test_host_base_minimal(self):
        """测试最小主机数据"""
        data = {'hostname': 'minimal-host', 'ip_address': '192.168.1.1', 'username': 'root'}
        schema = HostBase(**data)
        self.assertEqual(schema.hostname, 'minimal-host')
        self.assertEqual(schema.port, 22)  # 默认端口
        self.assertEqual(schema.status, 'offline')  # 默认状态
        self.assertEqual(schema.password, '')
        self.assertIsNone(schema.cluster)

    def test_host_create_request(self):
        """测试创建主机请求"""
        data = {
            'hostname': 'new-host',
            'ip_address': '192.168.1.50',
            'username': 'admin',
            'cluster': 1
        }
        schema = HostCreateRequest(**data)
        self.assertEqual(schema.hostname, 'new-host')

    def test_host_update_request(self):
        """测试更新主机请求"""
        data = {'hostname': 'updated-host', 'status': 'online'}
        schema = HostUpdateRequest(**data)
        self.assertEqual(schema.hostname, 'updated-host')
        self.assertEqual(schema.status, 'online')
        # 未提供的字段应为 None
        self.assertIsNone(schema.port)
        self.assertIsNone(schema.username)

    def test_host_update_request_partial(self):
        """测试部分更新主机请求"""
        data = {'status': 'offline'}
        schema = HostUpdateRequest(**data)
        self.assertEqual(schema.status, 'offline')
        self.assertIsNone(schema.hostname)

    def test_host_name_required(self):
        """测试主机名称为必填"""
        with self.assertRaises(Exception):
            HostBase(ip_address='192.168.1.1', username='root')

    def test_host_ip_required(self):
        """测试主机IP为必填"""
        with self.assertRaises(Exception):
            HostBase(hostname='test', username='root')

    def test_host_response(self):
        """测试主机响应模型"""
        data = {
            'id': 1,
            'hostname': 'response-host',
            'ip_address': '192.168.1.100',
            'port': 22,
            'username': 'admin',
            'cluster': 1,
            'cluster_name': 'TestCluster',
            'status': 'online',
            'os_type': 'CentOS 7',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = HostResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.cluster_name, 'TestCluster')


class VMSchemaTest(TestCase):
    """VM Schema 测试"""

    def test_vm_base_valid(self):
        """测试有效的VM基础模型"""
        data = {
            'name': 'test-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440000',
            'host': 1,
            'cluster': 1,
            'status': 'running',
            'vcpu': 4,
            'memory': 8589934592,
            'disk': 128849018880,
            'ip_address': '192.168.1.100',
            'mac_address': '00:0c:29:12:34:56',
            'os_type': 'Ubuntu 22.04'
        }
        schema = VMBase(**data)
        self.assertEqual(schema.name, 'test-vm')
        self.assertEqual(schema.uuid, '550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(schema.status, 'running')
        self.assertEqual(schema.vcpu, 4)

    def test_vm_base_minimal(self):
        """测试最小VM数据"""
        data = {'name': 'minimal-vm', 'uuid': 'uuid-minimal', 'host': 1}
        schema = VMBase(**data)
        self.assertEqual(schema.name, 'minimal-vm')
        self.assertEqual(schema.status, 'stopped')  # 默认状态
        self.assertEqual(schema.vcpu, 1)  # 默认CPU
        self.assertEqual(schema.memory, 0)
        self.assertEqual(schema.disk, 0)
        self.assertIsNone(schema.cluster)
        self.assertIsNone(schema.ip_address)

    def test_vm_create_request(self):
        """测试创建VM请求"""
        data = {
            'name': 'new-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440001',
            'host': 1,
            'cluster': 1,
            'vcpu': 8,
            'memory': 17179869184
        }
        schema = VMCreateRequest(**data)
        self.assertEqual(schema.name, 'new-vm')
        self.assertEqual(schema.vcpu, 8)
        self.assertEqual(schema.memory, 17179869184)

    def test_vm_update_request(self):
        """测试更新VM请求"""
        data = {'name': 'updated-vm', 'status': 'running', 'vcpu': 16}
        schema = VMUpdateRequest(**data)
        self.assertEqual(schema.name, 'updated-vm')
        self.assertEqual(schema.status, 'running')
        self.assertEqual(schema.vcpu, 16)
        # 未提供的字段应为 None
        self.assertIsNone(schema.host)
        self.assertIsNone(schema.memory)

    def test_vm_update_request_partial(self):
        """测试部分更新VM请求"""
        data = {'status': 'paused'}
        schema = VMUpdateRequest(**data)
        self.assertEqual(schema.status, 'paused')
        self.assertIsNone(schema.name)

    def test_vm_name_required(self):
        """测试VM名称为必填"""
        with self.assertRaises(Exception):
            VMBase(uuid='test-uuid', host=1)

    def test_vm_uuid_required(self):
        """测试VM UUID为必填"""
        with self.assertRaises(Exception):
            VMBase(name='test-vm', host=1)

    def test_vm_host_required(self):
        """测试VM宿主机为必填"""
        with self.assertRaises(Exception):
            VMBase(name='test-vm', uuid='test-uuid')

    def test_vm_response(self):
        """测试VM响应模型"""
        data = {
            'id': 1,
            'name': 'response-vm',
            'uuid': '550e8400-e29b-41d4-a716-446655440002',
            'host': 1,
            'host_name': 'vm-host',
            'cluster': 1,
            'cluster_name': 'VMCluster',
            'status': 'running',
            'vcpu': 4,
            'memory': 8589934592,
            'disk': 128849018880,
            'ip_address': '192.168.1.100',
            'mac_address': '00:0c:29:12:34:56',
            'os_type': 'Ubuntu 22.04',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z'
        }
        schema = VMResponse(**data)
        self.assertEqual(schema.id, 1)
        self.assertEqual(schema.host_name, 'vm-host')
        self.assertEqual(schema.cluster_name, 'VMCluster')

    def test_vm_status_choices(self):
        """测试VM状态枚举值"""
        for status in ['stopped', 'running', 'paused', 'suspended']:
            data = {'name': 'test', 'uuid': f'uuid-{status}', 'host': 1, 'status': status}
            schema = VMBase(**data)
            self.assertEqual(schema.status, status)
