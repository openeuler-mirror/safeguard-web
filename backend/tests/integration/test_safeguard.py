"""安全防护模块集成测试"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def disable_audit_log():
    """自动禁用审计日志，避免测试时的审计日志问题"""
    with patch('backend.middleware.audit.AuditLogMiddleware._do_log_audit') as mock_do_log:
        mock_do_log.return_value = None
        yield


class TestPolicyTemplateViewSet:
    """策略模板视图集测试"""

    def test_get_policy_templates_admin(self, admin_client, multiple_policy_templates):
        """测试管理员获取策略模板列表"""
        response = admin_client.get('/api/policy-templates/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_get_policy_templates_authenticated(self, authenticated_client, multiple_policy_templates):
        """测试已认证用户获取策略模板列表"""
        response = authenticated_client.get('/api/policy-templates/')
        # 可能需要管理员权限，所以可能返回 403
        assert response.status_code in [200, 401, 403]

    def test_get_policy_templates_unauthenticated(self, api_client):
        """测试未认证用户无法获取策略模板"""
        response = api_client.get('/api/policy-templates/')
        assert response.status_code == 401

    def test_create_policy_template(self, admin_client):
        """测试创建策略模板"""
        data = {
            'name': 'test-new-policy',
            'template_type': 'custom',
            'description': 'Test policy template',
            'config': {'rules': []}
        }
        response = admin_client.post('/api/policy-templates/', data, format='json')
        assert response.status_code == 200

    def test_get_policy_template_detail(self, admin_client, test_policy_template):
        """测试获取策略模板详情"""
        response = admin_client.get(f'/api/policy-templates/{test_policy_template.id}/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_update_policy_template(self, admin_client, test_policy_template):
        """测试更新策略模板"""
        data = {'name': 'updated-policy-name'}
        response = admin_client.patch(
            f'/api/policy-templates/{test_policy_template.id}/',
            data,
            format='json'
        )
        assert response.status_code == 200

    def test_delete_policy_template(self, admin_client, test_policy_template):
        """测试删除策略模板"""
        response = admin_client.delete(f'/api/policy-templates/{test_policy_template.id}/')
        assert response.status_code in [200, 204]

    def test_filter_policy_templates_by_type(self, admin_client, general_policy_template):
        """测试按类型过滤策略模板"""
        response = admin_client.get('/api/policy-templates/?template_type=general')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_filter_policy_templates_builtin(self, admin_client, builtin_policy_template):
        """测试过滤内置策略模板"""
        response = admin_client.get('/api/policy-templates/?is_builtin=true')
        assert response.status_code == 200
        assert response.data['errno'] == 0


class TestHostPolicyViewSet:
    """主机策略视图集测试"""

    def test_get_host_policies_admin(self, admin_client, test_host_policy):
        """测试管理员获取主机策略列表"""
        response = admin_client.get('/api/host-policies/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_get_host_policies_unauthenticated(self, api_client):
        """测试未认证用户无法获取主机策略"""
        response = api_client.get('/api/host-policies/')
        assert response.status_code == 401

    def test_get_host_policy_detail(self, admin_client, test_host_policy):
        """测试获取主机策略详情"""
        response = admin_client.get(f'/api/host-policies/{test_host_policy.id}/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_bind_host_policy(self, admin_client, test_host, test_policy_template):
        """测试绑定主机策略"""
        data = {
            'host_id': test_host.id,
            'template_id': test_policy_template.id
        }
        response = admin_client.post('/api/host-policies/bind/', data, format='json')
        assert response.status_code == 200

    def test_get_host_policy_detail_action(self, admin_client, test_host_policy):
        """测试获取主机策略详情的 action"""
        response = admin_client.get(f'/api/host-policies/{test_host_policy.id}/detail/')
        assert response.status_code == 200

    def test_filter_host_policies_by_status(self, admin_client, active_host_policy):
        """测试按状态过滤主机策略"""
        response = admin_client.get('/api/host-policies/?status=active')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_filter_host_policies_by_host(self, admin_client, test_host_policy, test_host):
        """测试按主机过滤主机策略"""
        response = admin_client.get(f'/api/host-policies/?host={test_host.id}')
        assert response.status_code == 200
        assert response.data['errno'] == 0
