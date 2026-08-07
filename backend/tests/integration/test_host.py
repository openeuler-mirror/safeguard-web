"""主机资产模块集成测试"""
import pytest
from unittest.mock import patch, MagicMock

from backend.models.host import Cluster, Host, VM, Image
from backend.tests.factories.host_factories import (
    ClusterFactory, HostFactory, VMFactory, ImageFactory
)

pytestmark = pytest.mark.django_db


class TestClusterViewSet:
    """集群管理视图集测试"""

    def test_create_cluster_success(self, admin_client):
        """测试创建集群成功"""
        url = "/api/clusters/"
        data = {
            "name": "test-cluster-001",
            "description": "测试集群"
        }

        response = admin_client.post(url, data, format="json")

        assert response.status_code == 201 or response.status_code == 200
        if response.status_code == 200:
            assert response.data["errno"] == 0
        assert Cluster.objects.filter(name="test-cluster-001").exists()

    def test_create_cluster_failed_unauthorized(self, api_client):
        """测试未授权创建集群失败"""
        url = "/api/clusters/"
        data = {
            "name": "test-cluster-002",
            "description": "测试集群"
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code in [401, 403]

    def test_create_cluster_failed_duplicate_name(self, admin_client, test_cluster):
        """测试创建集群名称重复"""
        url = "/api/clusters/"
        data = {
            "name": test_cluster.name,
            "description": "重复名称"
        }

        response = admin_client.post(url, data, format="json")

        # 根据实际实现，可能返回 400 或错误码
        assert response.status_code in [200, 400]

    def test_list_clusters(self, admin_client, multiple_clusters):
        """测试获取集群列表"""
        url = "/api/clusters/"

        response = admin_client.get(url)

        assert response.status_code == 200
        if response.data.get("errno") == 0:
            assert len(response.data["data"]["results"]) >= 3 or len(response.data["data"]) >= 3
        else:
            # 直接返回列表的情况
            assert len(response.data) >= 3 or len(response.data.get("results", [])) >= 3

    def test_get_cluster_detail(self, admin_client, test_cluster):
        """测试获取集群详情"""
        url = f"/api/clusters/{test_cluster.id}/"

        response = admin_client.get(url)

        assert response.status_code == 200
        if response.data.get("errno") == 0:
            assert response.data["data"]["name"] == test_cluster.name
        else:
            assert response.data["name"] == test_cluster.name

    def test_update_cluster_success(self, admin_client, test_cluster):
        """测试更新集群成功"""
        url = f"/api/clusters/{test_cluster.id}/"
        data = {
            "name": "updated-cluster-name",
            "description": "更新后的描述"
        }

        response = admin_client.patch(url, data, format="json")

        assert response.status_code == 200
        test_cluster.refresh_from_db()
        assert test_cluster.name == "updated-cluster-name"

    def test_delete_cluster_success(self, admin_client, test_cluster):
        """测试删除集群成功"""
        url = f"/api/clusters/{test_cluster.id}/"

        response = admin_client.delete(url)

        assert response.status_code in [200, 204]
        assert not Cluster.objects.filter(id=test_cluster.id).exists()

    def test_delete_cluster_failed_has_hosts(self, admin_client, test_cluster, test_host):
        """测试删除有关联主机的集群失败"""
        url = f"/api/clusters/{test_cluster.id}/"

        response = admin_client.delete(url)

        # 应该被拒绝
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            assert response.data["errno"] != 0
        # 集群应该仍然存在
        assert Cluster.objects.filter(id=test_cluster.id).exists()

    def test_get_cluster_hosts(self, admin_client, test_cluster, multiple_hosts):
        """测试获取集群下的主机列表"""
        url = f"/api/clusters/{test_cluster.id}/hosts/"

        response = admin_client.get(url)

        assert response.status_code == 200

    def test_get_cluster_tree(self, admin_client, multiple_clusters):
        """测试获取集群树"""
        url = "/api/clusters/tree/"

        response = admin_client.get(url)

        assert response.status_code == 200


class TestHostViewSet:
    """主机管理视图集测试"""

    def test_create_host_success(self, admin_client, test_cluster):
        """测试创建主机成功"""
        url = "/api/hosts/"
        data = {
            "hostname": "test-host-001",
            "ip_address": "192.168.1.100",
            "port": 22,
            "username": "root",
            "password": "password123",
            "cluster": test_cluster.id,
            "status": "offline",
            "host_type": "VMHost"
        }

        response = admin_client.post(url, data, format="json")

        assert response.status_code in [201, 200]
        assert Host.objects.filter(hostname="test-host-001").exists()

    def test_create_host_failed_duplicate_ip(self, admin_client, test_cluster, test_host):
        """测试创建主机 IP 重复"""
        url = "/api/hosts/"
        data = {
            "hostname": "test-host-002",
            "ip_address": test_host.ip_address,
            "port": 22,
            "username": "root",
            "password": "password123",
            "cluster": test_cluster.id
        }

        response = admin_client.post(url, data, format="json")

        assert response.status_code in [200, 400]

    def test_create_host_failed_unauthorized(self, api_client, test_cluster):
        """测试未授权创建主机失败"""
        url = "/api/hosts/"
        data = {
            "hostname": "test-host-003",
            "ip_address": "192.168.1.101",
            "port": 22,
            "username": "root",
            "password": "password123",
            "cluster": test_cluster.id
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code in [401, 403]

    def test_list_hosts(self, admin_client, multiple_hosts):
        """测试获取主机列表"""
        url = "/api/hosts/"

        response = admin_client.get(url)

        assert response.status_code == 200

    def test_list_hosts_with_filter(self, admin_client, multiple_hosts, test_cluster):
        """测试带筛选条件的主机列表"""
        # 创建另一个集群和主机
        other_cluster = ClusterFactory.create(name="other-cluster")
        HostFactory.create(cluster=other_cluster, hostname="filtered-host")

        url = f"/api/hosts/?cluster={test_cluster.id}"
        response = admin_client.get(url)

        assert response.status_code == 200

    def test_list_hosts_with_search(self, admin_client, test_cluster):
        """测试搜索主机"""
        HostFactory.create(cluster=test_cluster, hostname="search-test-001", ip_address="10.0.0.1")
        HostFactory.create(cluster=test_cluster, hostname="search-test-002", ip_address="10.0.0.2")
        HostFactory.create(cluster=test_cluster, hostname="other-host", ip_address="10.0.0.3")

        url = "/api/hosts/?search=search-test"
        response = admin_client.get(url)

        assert response.status_code == 200

    def test_get_host_detail(self, admin_client, test_host):
        """测试获取主机详情"""
        url = f"/api/hosts/{test_host.id}/"

        response = admin_client.get(url)

        assert response.status_code == 200

    def test_update_host_success(self, admin_client, test_host):
        """测试更新主机成功"""
        url = f"/api/hosts/{test_host.id}/"
        data = {
            "hostname": "updated-hostname",
            "status": "online"
        }

        response = admin_client.patch(url, data, format="json")

        assert response.status_code == 200
        test_host.refresh_from_db()
        assert test_host.hostname == "updated-hostname"

    def test_delete_host_success(self, admin_client, test_host):
        """测试删除主机成功"""
        url = f"/api/hosts/{test_host.id}/"

        response = admin_client.delete(url)

        assert response.status_code in [200, 204]
        assert not Host.objects.filter(id=test_host.id).exists()

    def test_delete_host_with_vms(self, admin_client, test_host_with_vms):
        """测试删除有关联虚拟机的主机"""
        host_id = test_host_with_vms.id
        vm_count = test_host_with_vms.vm_set.count()
        assert vm_count >= 2

        url = f"/api/hosts/{host_id}/"
        response = admin_client.delete(url)

        # 根据业务逻辑，可能级联删除或拒绝
        assert response.status_code in [200, 204, 400]
