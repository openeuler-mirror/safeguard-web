"""pytest 全局配置和 fixtures"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from backend.tests.factories.user_factories import (
    UserFactory, AuthorityFactory, MenuFactory, UserAuthorityFactory
)
from backend.tests.factories.host_factories import (
    ClusterFactory, HostFactory, VMFactory, ImageFactory
)


@pytest.fixture
def api_client():
    """未认证的 API 客户端"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """普通测试用户"""
    return UserFactory.create(password="testpass123")


@pytest.fixture
def authenticated_client(api_client, test_user):
    """已认证的 API 客户端"""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_user(db):
    """管理员用户"""
    return UserFactory.create_admin(password="admin123")


@pytest.fixture
def admin_client(api_client, admin_user):
    """管理员认证客户端"""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def test_authority(db):
    """测试角色"""
    return AuthorityFactory.create()


@pytest.fixture
def test_user_with_authority(db, test_user, test_authority):
    """带角色的用户"""
    UserAuthorityFactory.create(user=test_user, authority=test_authority)
    return test_user


@pytest.fixture
def test_cluster(db):
    """测试集群"""
    return ClusterFactory.create()


@pytest.fixture
def multiple_clusters(db):
    """多个测试集群"""
    return ClusterFactory.create_batch(3)


@pytest.fixture
def test_host(db, test_cluster):
    """测试宿主机"""
    return HostFactory.create(cluster=test_cluster)


@pytest.fixture
def test_host_with_vms(db, test_cluster):
    """带虚拟机的测试宿主机"""
    return HostFactory.create_with_vms(cluster=test_cluster, vm_count=2)


@pytest.fixture
def multiple_hosts(db, test_cluster):
    """多个测试宿主机"""
    return HostFactory.create_batch(5, cluster=test_cluster)
