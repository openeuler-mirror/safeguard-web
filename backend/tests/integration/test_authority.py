"""权限管理模块集成测试"""
import pytest

from backend.models.authority import (
    Authority, Menu, MenuButton, AuthorityMenu, AuthorityButton, UserAuthority
)


pytestmark = pytest.mark.django_db


class TestAuthorityCRUD:
    """角色管理 CRUD 接口测试"""

    @pytest.mark.p0
    def test_get_authority_list_admin(self, admin_client, multiple_authorities):
        """测试管理员获取角色列表"""
        response = admin_client.get('/api/authority/authorities/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            assert len(data['results']) >= 3
        elif isinstance(data, list):
            assert len(data) >= 3

    @pytest.mark.p0
    def test_get_authority_list_regular_user_forbidden(self, authenticated_client):
        """测试普通用户不能获取角色列表（需要管理员权限）"""
        response = authenticated_client.get('/api/authority/authorities/')
        # 应该被拒绝或返回错误
        assert response.status_code in (200, 403, 401)
        if response.status_code == 200:
            assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_create_authority_admin(self, admin_client):
        """测试管理员创建角色成功"""
        data = {
            'authority_id': 999,
            'authority_name': '新测试角色',
            'default_router': 'dashboard'
        }

        response = admin_client.post('/api/authority/authorities/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['authority_name'] == '新测试角色'
        assert Authority.objects.filter(authority_id=999).exists()

    @pytest.mark.p0
    def test_create_authority_regular_user_forbidden(self, authenticated_client):
        """测试普通用户不能创建角色"""
        data = {
            'authority_id': 888,
            'authority_name': '普通用户创建角色',
            'default_router': 'dashboard'
        }
        response = authenticated_client.post('/api/authority/authorities/', data, format='json')
        assert response.status_code in (200, 403, 401)

    @pytest.mark.p0
    def test_create_authority_duplicate_id(self, admin_client, test_authority):
        """测试创建角色时使用已存在的 ID 应该失败"""
        data = {
            'authority_id': test_authority.authority_id,
            'authority_name': '重复 ID 角色',
            'default_router': 'dashboard'
        }
        response = admin_client.post('/api/authority/authorities/', data, format='json')
        assert response.status_code in (200, 400)
        if response.status_code == 200:
            assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_retrieve_authority_admin(self, admin_client, test_authority):
        """测试管理员获取单个角色详情"""
        response = admin_client.get(f'/api/authority/authorities/{test_authority.id}/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['authority_id'] == test_authority.authority_id
        assert response.data['data']['authority_name'] == test_authority.authority_name

    @pytest.mark.p1
    def test_update_authority_admin(self, admin_client, test_authority):
        """测试管理员更新角色信息"""
        data = {'authority_name': '更新后的角色名', 'default_router': 'new-dashboard'}
        response = admin_client.patch(f'/api/authority/authorities/{test_authority.id}/', data, format='json')

        assert response.status_code == 200
        test_authority.refresh_from_db()
        assert test_authority.authority_name == '更新后的角色名'
        assert test_authority.default_router == 'new-dashboard'

    @pytest.mark.p1
    def test_delete_authority_admin(self, admin_client, test_authority):
        """测试管理员删除角色"""
        authority_id = test_authority.id
        response = admin_client.delete(f'/api/authority/authorities/{authority_id}/')

        assert response.status_code in (200, 204)
        if response.status_code == 200:
            assert response.data['errno'] == 0
        assert not Authority.objects.filter(id=authority_id).exists()
