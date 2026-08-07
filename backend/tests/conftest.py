"""pytest 全局配置和 fixtures"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from backend.tests.factories.user_factories import (
    UserFactory, AuthorityFactory, MenuFactory, UserAuthorityFactory, MenuButtonFactory
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
def frozen_user(db):
    """被冻结的用户"""
    return UserFactory.create_frozen(password="testpass123")


@pytest.fixture
def multiple_users(db):
    """多个测试用户"""
    return UserFactory.create_batch(5)


@pytest.fixture
def test_menu(db):
    """测试菜单"""
    return MenuFactory.create()


@pytest.fixture
def test_menu_tree(db):
    """测试菜单树"""
    root = MenuFactory.create(path="/test", name="TestRoot")
    child1 = MenuFactory.create(parent=root, path="/test/child1", name="TestChild1")
    child2 = MenuFactory.create(parent=root, path="/test/child2", name="TestChild2")
    return root


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


@pytest.fixture
def test_vm(db, test_host):
    """测试虚拟机"""
    return VMFactory.create(host=test_host)


@pytest.fixture
def multiple_vms(db, test_host):
    """多个测试虚拟机"""
    return VMFactory.create_batch(3, host=test_host)


@pytest.fixture
def test_image(db, test_host):
    """测试镜像"""
    return ImageFactory.create(host=test_host)


@pytest.fixture
def clear_redis():
    """清除 Redis 缓存"""
    from backend.authentication import redis_client

    def _clear_user_redis(user_id):
        redis_client.delete(f'user:{user_id}')

    return _clear_user_redis


@pytest.fixture
def multiple_authorities(db):
    """多个测试角色"""
    return AuthorityFactory.create_batch(3, start_id=200)


@pytest.fixture
def authority_with_menu(db):
    """带菜单权限的角色"""
    return AuthorityFactory.create_with_menu(authority_id=300, menu_count=2)


@pytest.fixture
def authority_with_button(db):
    """带按钮权限的角色"""
    return AuthorityFactory.create_with_button(authority_id=400, button_count=2)


@pytest.fixture
def test_menu_button(db, test_menu):
    """测试菜单按钮"""
    return MenuButtonFactory.create(menu=test_menu)


@pytest.fixture
def multiple_menus(db):
    """多个测试菜单"""
    return [
        MenuFactory.create(path=f"/menu-{i}", name=f"Menu{i}")
        for i in range(3)
    ]
