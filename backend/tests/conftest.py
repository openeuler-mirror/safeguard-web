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
from backend.tests.factories.osdeploy_factories import (
    JobStatusFactory, RepoStatusFactory, WhiteListFactory,
    PXEServerStatusFactory, KickStartFileStatusFactory, ISOFileStatusFactory,
    OutIpSNFactory, SensorDataFactory
)
from backend.tests.factories.safeguard_factories import (
    SafeguardPolicyTemplateFactory, HostSafeguardPolicyFactory,
    PolicyApplyTaskFactory, HostMonitorDataFactory,
    FileMonitorRuleFactory, FileMonitorEventFactory,
    AuditLogFactory, SystemLogFactory
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


# ============ OS Deploy Fixtures ============
@pytest.fixture
def test_job(db):
    """测试部署任务"""
    return JobStatusFactory.create()


@pytest.fixture
def multiple_jobs(db):
    """多个部署任务"""
    return JobStatusFactory.create_batch(5)


@pytest.fixture
def running_job(db):
    """运行中的任务"""
    return JobStatusFactory.create_running()


@pytest.fixture
def success_job(db):
    """成功的任务"""
    return JobStatusFactory.create_success()


@pytest.fixture
def failed_job(db):
    """失败的任务"""
    return JobStatusFactory.create_failed()


@pytest.fixture
def test_repo(db):
    """测试仓库"""
    return RepoStatusFactory.create()


@pytest.fixture
def multiple_repos(db):
    """多个测试仓库"""
    return RepoStatusFactory.create_batch(3)


@pytest.fixture
def default_repo(db):
    """默认仓库"""
    return RepoStatusFactory.create_default()


@pytest.fixture
def test_whitelist(db):
    """测试白名单"""
    return WhiteListFactory.create()


@pytest.fixture
def multiple_whitelists(db):
    """多个白名单"""
    return WhiteListFactory.create_batch(3)


@pytest.fixture
def test_pxe_server(db):
    """测试PXE服务器"""
    return PXEServerStatusFactory.create()


@pytest.fixture
def multiple_pxe_servers(db):
    """多个PXE服务器"""
    return PXEServerStatusFactory.create_batch(2)


@pytest.fixture
def test_kickstart(db):
    """测试Kickstart文件"""
    return KickStartFileStatusFactory.create()


@pytest.fixture
def test_iso(db):
    """测试ISO文件"""
    return ISOFileStatusFactory.create()


@pytest.fixture
def test_outipsn(db):
    """测试出口IP序列号"""
    return OutIpSNFactory.create()


@pytest.fixture
def test_sensor_data(db):
    """测试传感器数据"""
    return SensorDataFactory.create()


# ============ Safeguard Fixtures ============
@pytest.fixture
def test_policy_template(db):
    """测试策略模板"""
    return SafeguardPolicyTemplateFactory.create()


@pytest.fixture
def multiple_policy_templates(db):
    """多个策略模板"""
    return SafeguardPolicyTemplateFactory.create_batch(3)


@pytest.fixture
def builtin_policy_template(db):
    """内置策略模板"""
    return SafeguardPolicyTemplateFactory.create_builtin()


@pytest.fixture
def general_policy_template(db):
    """通用防护模板"""
    return SafeguardPolicyTemplateFactory.create_general()


@pytest.fixture
def test_host_policy(db, test_host, test_policy_template):
    """测试主机策略"""
    return HostSafeguardPolicyFactory.create(
        host=test_host,
        template=test_policy_template
    )


@pytest.fixture
def active_host_policy(db, test_host, test_policy_template):
    """已生效主机策略"""
    return HostSafeguardPolicyFactory.create_active(
        host=test_host,
        template=test_policy_template
    )


@pytest.fixture
def test_policy_task(db, test_host, test_host_policy, admin_user):
    """测试策略任务"""
    return PolicyApplyTaskFactory.create(
        host=test_host,
        policy=test_host_policy,
        created_by=admin_user
    )


@pytest.fixture
def running_policy_task(db, test_host, test_host_policy, admin_user):
    """运行中的策略任务"""
    return PolicyApplyTaskFactory.create_running(
        host=test_host,
        policy=test_host_policy,
        created_by=admin_user
    )


@pytest.fixture
def success_policy_task(db, test_host, test_host_policy, admin_user):
    """成功的策略任务"""
    return PolicyApplyTaskFactory.create_success(
        host=test_host,
        policy=test_host_policy,
        created_by=admin_user
    )


@pytest.fixture
def test_monitor_data(db, test_host):
    """测试监控数据"""
    return HostMonitorDataFactory.create(host=test_host)


@pytest.fixture
def multiple_monitor_data(db, test_host):
    """多个监控数据"""
    return HostMonitorDataFactory.create_batch(5, host=test_host)


@pytest.fixture
def test_file_monitor_rule(db, test_host):
    """测试文件监控规则"""
    return FileMonitorRuleFactory.create(host=test_host)


@pytest.fixture
def multiple_file_monitor_rules(db, test_host):
    """多个文件监控规则"""
    return FileMonitorRuleFactory.create_batch(3, host=test_host)


@pytest.fixture
def test_file_monitor_event(db, test_host, test_file_monitor_rule):
    """测试文件监控事件"""
    return FileMonitorEventFactory.create(
        host=test_host,
        rule=test_file_monitor_rule
    )


@pytest.fixture
def test_audit_log(db, admin_user):
    """测试审计日志"""
    return AuditLogFactory.create(user=admin_user)


@pytest.fixture
def multiple_audit_logs(db, admin_user):
    """多个审计日志"""
    return AuditLogFactory.create_batch(5, user=admin_user)


@pytest.fixture
def login_audit_log(db, admin_user):
    """登录审计日志"""
    return AuditLogFactory.create_login(user=admin_user)


@pytest.fixture
def test_system_log(db, test_host):
    """测试系统日志"""
    return SystemLogFactory.create(host=test_host)


@pytest.fixture
def multiple_system_logs(db, test_host):
    """多个系统日志"""
    return SystemLogFactory.create_batch(5, host=test_host)


@pytest.fixture
def error_system_log(db, test_host):
    """错误系统日志"""
    return SystemLogFactory.create_error(host=test_host)
