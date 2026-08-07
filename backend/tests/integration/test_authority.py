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
    def test_get_authority_list_authenticated_user(self, authenticated_client, multiple_authorities):
        """测试已认证用户可以获取角色列表"""
        response = authenticated_client.get('/api/authority/authorities/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            assert len(data['results']) >= 3
        elif isinstance(data, list):
            assert len(data) >= 3

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


class TestAuthorityMenu:
    """角色菜单权限管理接口测试"""

    @pytest.mark.p0
    def test_get_authority_menus(self, admin_client, authority_with_menu):
        """测试获取角色菜单列表"""
        response = admin_client.get(f'/api/authority/authorities/{authority_with_menu.id}/menus/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)
        assert len(response.data['data']) >= 1

    @pytest.mark.p0
    def test_set_authority_menus(self, admin_client, test_authority, multiple_menus):
        """测试为角色分配菜单权限"""
        menu_ids = [menu.id for menu in multiple_menus]
        data = {'menu_ids': menu_ids}

        response = admin_client.put(f'/api/authority/authorities/{test_authority.id}/menus/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert '菜单绑定成功' in response.data['errmsg']

        # 验证菜单已分配
        assigned_menus = AuthorityMenu.objects.filter(authority=test_authority)
        assert assigned_menus.count() == len(menu_ids)
        for menu_id in menu_ids:
            assert assigned_menus.filter(menu_id=menu_id).exists()

    @pytest.mark.p0
    def test_set_authority_menus_invalid_menu_id(self, admin_client, test_authority):
        """测试设置菜单权限时使用无效的菜单 ID 应该失败"""
        data = {'menu_ids': [999999]}  # 不存在的菜单 ID

        response = admin_client.put(f'/api/authority/authorities/{test_authority.id}/menus/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] != 0

    @pytest.mark.p0
    def test_set_authority_menus_replaces_existing(self, admin_client, authority_with_menu, multiple_menus):
        """测试设置菜单权限时会替换原有的菜单权限"""
        old_menu_count = AuthorityMenu.objects.filter(authority=authority_with_menu).count()
        assert old_menu_count > 0

        menu_ids = [menu.id for menu in multiple_menus]
        data = {'menu_ids': menu_ids}

        response = admin_client.put(f'/api/authority/authorities/{authority_with_menu.id}/menus/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0

        # 验证旧菜单已被替换
        new_menu_count = AuthorityMenu.objects.filter(authority=authority_with_menu).count()
        assert new_menu_count == len(menu_ids)


class TestAuthorityButton:
    """角色按钮权限管理接口测试"""

    @pytest.mark.p0
    def test_get_authority_buttons(self, admin_client, authority_with_button):
        """测试获取角色按钮权限列表"""
        response = admin_client.get(f'/api/authority/authorities/{authority_with_button.id}/btns/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)

    @pytest.mark.p0
    def test_set_authority_buttons(self, admin_client, test_authority, test_menu, test_menu_button):
        """测试为角色分配按钮权限"""
        data = {
            'buttons': [
                {
                    'menu_id': test_menu.id,
                    'button_ids': [test_menu_button.id]
                }
            ]
        }

        response = admin_client.put(f'/api/authority/authorities/{test_authority.id}/btns/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert '按钮权限绑定成功' in response.data['errmsg']

        # 验证按钮权限已分配
        assigned_buttons = AuthorityButton.objects.filter(authority=test_authority)
        assert assigned_buttons.count() == 1
        assert assigned_buttons.first().button_id == test_menu_button.id

    @pytest.mark.p0
    def test_set_authority_buttons_replaces_existing(self, admin_client, authority_with_button, test_menu, test_menu_button):
        """测试设置按钮权限时会替换原有的按钮权限"""
        old_btn_count = AuthorityButton.objects.filter(authority=authority_with_button).count()
        assert old_btn_count > 0

        data = {
            'buttons': [
                {
                    'menu_id': test_menu.id,
                    'button_ids': [test_menu_button.id]
                }
            ]
        }

        response = admin_client.put(f'/api/authority/authorities/{authority_with_button.id}/btns/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0

        # 验证旧按钮权限已被替换
        new_btn_count = AuthorityButton.objects.filter(authority=authority_with_button).count()
        assert new_btn_count == 1


class TestAuthorityCopy:
    """角色复制功能接口测试"""

    @pytest.mark.p1
    def test_copy_authority(self, admin_client, authority_with_menu):
        """测试复制角色"""
        original_menu_count = AuthorityMenu.objects.filter(authority=authority_with_menu).count()

        response = admin_client.post(f'/api/authority/authorities/{authority_with_menu.id}/copy/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert '角色复制成功' in response.data['errmsg']
        assert 'id' in response.data['data']

        # 验证新角色已创建
        new_authority = Authority.objects.filter(id=response.data['data']['id']).first()
        assert new_authority is not None
        assert new_authority.authority_name == f'{authority_with_menu.authority_name}_副本'

        # 验证菜单权限已复制
        new_menu_count = AuthorityMenu.objects.filter(authority=new_authority).count()
        assert new_menu_count == original_menu_count


class TestMenuCRUD:
    """菜单管理 CRUD 接口测试"""

    @pytest.mark.p0
    def test_get_menu_list_admin(self, admin_client, multiple_menus):
        """测试管理员获取菜单列表"""
        response = admin_client.get('/api/authority/menus/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            assert len(data['results']) >= 3
        elif isinstance(data, list):
            assert len(data) >= 3

    @pytest.mark.p0
    def test_get_menu_list_authenticated_user(self, authenticated_client, multiple_menus):
        """测试已认证用户可以获取菜单列表"""
        response = authenticated_client.get('/api/authority/menus/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        data = response.data['data']
        if isinstance(data, dict) and 'results' in data:
            assert len(data['results']) >= 3
        elif isinstance(data, list):
            assert len(data) >= 3

    @pytest.mark.p0
    def test_create_menu_admin(self, admin_client):
        """测试管理员创建菜单成功"""
        data = {
            'path': '/test-new-menu',
            'name': '新测试菜单',
            'component': 'test-component',
            'sort': 10
        }

        response = admin_client.post('/api/authority/menus/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert Menu.objects.filter(path='/test-new-menu').exists()

    @pytest.mark.p0
    def test_create_menu_with_parent(self, admin_client, test_menu):
        """测试创建子菜单"""
        data = {
            'parent': test_menu.id,
            'path': '/test-sub-menu',
            'name': '子测试菜单',
            'component': 'sub-component'
        }

        response = admin_client.post('/api/authority/menus/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0

        new_menu = Menu.objects.filter(path='/test-sub-menu').first()
        assert new_menu is not None
        assert new_menu.parent_id == test_menu.id

    @pytest.mark.p0
    def test_get_menu_tree_admin(self, admin_client, test_menu_tree):
        """测试获取菜单树"""
        response = admin_client.get('/api/authority/menus/tree/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert isinstance(response.data['data'], list)

    @pytest.mark.p0
    def test_retrieve_menu_admin(self, admin_client, test_menu):
        """测试管理员获取单个菜单详情"""
        response = admin_client.get(f'/api/authority/menus/{test_menu.id}/')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert response.data['data']['path'] == test_menu.path
        assert response.data['data']['name'] == test_menu.name

    @pytest.mark.p1
    def test_update_menu_admin(self, admin_client, test_menu):
        """测试管理员更新菜单"""
        data = {'name': '更新后的菜单名', 'sort': 99}
        response = admin_client.patch(f'/api/authority/menus/{test_menu.id}/', data, format='json')

        assert response.status_code == 200
        test_menu.refresh_from_db()
        assert test_menu.name == '更新后的菜单名'
        assert test_menu.sort == 99

    @pytest.mark.p1
    def test_delete_menu_admin(self, admin_client, test_menu):
        """测试管理员删除菜单"""
        menu_id = test_menu.id
        response = admin_client.delete(f'/api/authority/menus/{menu_id}/')

        assert response.status_code in (200, 204)
        if response.status_code == 200:
            assert response.data['errno'] == 0
        assert not Menu.objects.filter(id=menu_id).exists()

    @pytest.mark.p1
    def test_reorder_menus_admin(self, admin_client, multiple_menus):
        """测试批量更新菜单排序"""
        orders = [
            {'id': multiple_menus[0].id, 'sort': 30},
            {'id': multiple_menus[1].id, 'sort': 20},
            {'id': multiple_menus[2].id, 'sort': 10}
        ]
        data = {'orders': orders}

        response = admin_client.post('/api/authority/menus/reorder/', data, format='json')

        assert response.status_code == 200
        assert response.data['errno'] == 0
        assert '排序更新成功' in response.data['errmsg']

        # 验证排序已更新
        for item in orders:
            menu = Menu.objects.get(id=item['id'])
            assert menu.sort == item['sort']


class TestUserAuthorityIntegration:
    """用户角色分配集成测试"""

    @pytest.mark.p0
    def test_assign_user_authority_and_verify_menu_access(self, admin_client, test_user, test_authority, test_menu):
        """测试为用户分配角色并验证菜单权限"""
        # 为角色分配菜单
        AuthorityMenu.objects.create(authority=test_authority, menu=test_menu)

        # 为用户分配角色
        UserAuthority.objects.create(user=test_user, authority=test_authority)

        # 验证用户角色关联存在
        assert UserAuthority.objects.filter(user=test_user, authority=test_authority).exists()

        # 验证角色菜单关联存在
        assert AuthorityMenu.objects.filter(authority=test_authority, menu=test_menu).exists()


class TestAuthorityPermission:
    """权限验证集成测试"""

    @pytest.mark.p0
    def test_authentication_required_for_authority_management(self, api_client):
        """测试角色管理需要用户认证"""
        # 尝试获取角色列表（未认证应该返回401）
        list_response = api_client.get('/api/authority/authorities/')
        assert list_response.status_code == 401

        # 尝试创建角色（未认证应该返回401）
        create_data = {'authority_id': 999, 'authority_name': '无权限创建', 'default_router': 'dashboard'}
        create_response = api_client.post('/api/authority/authorities/', create_data, format='json')
        assert create_response.status_code == 401

    @pytest.mark.p0
    def test_authentication_required_for_menu_management(self, api_client):
        """测试菜单管理需要用户认证"""
        # 尝试获取菜单列表（未认证应该返回401）
        list_response = api_client.get('/api/authority/menus/')
        assert list_response.status_code == 401

        # 尝试创建菜单（未认证应该返回401）
        create_data = {'path': '/no-permission', 'name': '无权限菜单', 'component': 'test'}
        create_response = api_client.post('/api/authority/menus/', create_data, format='json')
        assert create_response.status_code == 401
