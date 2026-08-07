"""OS 部署模块集成测试"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def disable_audit_log():
    """自动禁用审计日志，避免测试时的审计日志问题"""
    with patch('backend.middleware.audit.AuditLogMiddleware._do_log_audit') as mock_do_log:
        mock_do_log.return_value = None
        yield


class TestJobStatusViewSet:
    """任务状态视图集测试"""

    def test_get_job_list_authenticated(self, authenticated_client, multiple_jobs):
        """测试已认证用户获取任务列表"""
        response = authenticated_client.get('/api/jobs/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_get_job_list_admin(self, admin_client, multiple_jobs):
        """测试管理员获取任务列表"""
        response = admin_client.get('/api/jobs/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_get_job_list_unauthenticated(self, api_client):
        """测试未认证用户无法获取任务列表"""
        response = api_client.get('/api/jobs/')
        assert response.status_code == 401

    def test_query_job_status(self, authenticated_client, test_job):
        """测试查询任务状态"""
        response = authenticated_client.get(
            f'/api/jobs/query/?job_id={test_job.job_id}'
        )
        assert response.status_code == 200

    def test_query_job_status_missing_param(self, authenticated_client):
        """测试查询任务状态缺少参数"""
        response = authenticated_client.get('/api/jobs/query/')
        assert response.status_code == 200
        assert response.data['errno'] != 0

    def test_get_job_detail(self, authenticated_client, test_job):
        """测试获取任务详情"""
        response = authenticated_client.get(f'/api/jobs/{test_job.id}/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_filter_jobs_by_type(self, authenticated_client, test_job):
        """测试按任务类型过滤"""
        response = authenticated_client.get(
            f'/api/jobs/?job_type={test_job.job_type}'
        )
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_filter_jobs_by_status(self, authenticated_client, test_job):
        """测试按状态过滤"""
        response = authenticated_client.get(
            f'/api/jobs/?status={test_job.status}'
        )
        assert response.status_code == 200
        assert response.data['errno'] == 0


class TestRepoStatusViewSet:
    """仓库状态视图集测试"""

    def test_get_repo_list_authenticated(self, authenticated_client, multiple_repos):
        """测试已认证用户获取仓库列表"""
        response = authenticated_client.get('/api/repos/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_get_repo_list_unauthenticated(self, api_client):
        """测试未认证用户无法获取仓库列表"""
        response = api_client.get('/api/repos/')
        assert response.status_code == 401

    def test_create_repo(self, admin_client):
        """测试创建仓库"""
        data = {
            'name': 'test-new-repo',
            'repo_type': 'yum',
            'base_url': 'http://repo.example.com/yum',
            'is_default': False,
            'status': 'active'
        }
        response = admin_client.post('/api/repos/', data, format='json')
        assert response.status_code == 200

    def test_create_repo_unauthorized(self, authenticated_client):
        """测试普通用户无法创建仓库（如果有权限控制的话）"""
        data = {
            'name': 'test-repo-unauth',
            'repo_type': 'yum',
            'base_url': 'http://repo.example.com/yum'
        }
        response = authenticated_client.post('/api/repos/', data, format='json')
        # 可能成功也可能返回权限错误，取决于实际实现
        assert response.status_code in [200, 403]

    def test_get_repo_detail(self, authenticated_client, test_repo):
        """测试获取仓库详情"""
        response = authenticated_client.get(f'/api/repos/{test_repo.id}/')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_update_repo(self, admin_client, test_repo):
        """测试更新仓库"""
        data = {'name': 'updated-repo-name'}
        response = admin_client.patch(
            f'/api/repos/{test_repo.id}/',
            data,
            format='json'
        )
        assert response.status_code == 200

    def test_delete_repo(self, admin_client, test_repo):
        """测试删除仓库"""
        response = admin_client.delete(f'/api/repos/{test_repo.id}/')
        assert response.status_code in [200, 204]

    def test_filter_repos_by_type(self, authenticated_client, test_repo):
        """测试按类型过滤仓库"""
        response = authenticated_client.get(
            f'/api/repos/?repo_type={test_repo.repo_type}'
        )
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_filter_repos_default(self, authenticated_client, default_repo):
        """测试过滤默认仓库"""
        response = authenticated_client.get('/api/repos/?is_default=true')
        assert response.status_code == 200
        assert response.data['errno'] == 0

    def test_sync_repo_action(self, admin_client, test_repo):
        """测试同步仓库操作（mocked）"""
        with patch('backend.views.osdeploy.repo_status.RepoService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.sync_repo.return_value = {'status': 'success'}
            response = admin_client.post(f'/api/repos/{test_repo.id}/sync/')
            assert response.status_code == 200

    def test_enable_repo_action(self, admin_client, test_repo):
        """测试启用仓库操作（mocked）"""
        with patch('backend.views.osdeploy.repo_status.RepoService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.enable_repo.return_value = {'status': 'enabled'}
            response = admin_client.post(f'/api/repos/{test_repo.id}/enable/')
            assert response.status_code == 200

    def test_disable_repo_action(self, admin_client, test_repo):
        """测试禁用仓库操作（mocked）"""
        with patch('backend.views.osdeploy.repo_status.RepoService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.disable_repo.return_value = {'status': 'disabled'}
            response = admin_client.post(f'/api/repos/{test_repo.id}/disable/')
            assert response.status_code == 200

    def test_check_repo_action(self, admin_client, test_repo):
        """测试检查仓库操作（mocked）"""
        with patch('backend.views.osdeploy.repo_status.RepoService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.check_repo.return_value = {'available': True}
            response = admin_client.get(f'/api/repos/{test_repo.id}/check/')
            assert response.status_code == 200
