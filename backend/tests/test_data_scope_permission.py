"""数据权限 (DataScopePermission) 测试"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority, Cluster, Host
from backend.permissions.base import DataScopePermission


class DataScopePermissionUnitTest(TestCase):
    """DataScopePermission 单元测试"""

    def setUp(self):
        # 创建角色：R1 -> data_authority -> R2
        self.r1 = Authority.objects.create(authority_id=1, authority_name='R1')
        self.r2 = Authority.objects.create(authority_id=2, authority_name='R2')
        self.r3 = Authority.objects.create(authority_id=3, authority_name='R3')
        self.r1.data_authority = self.r2
        self.r1.save()

        # 创建用户
        self.user_a = Users.objects.create(user='user_a', password='pass')
        self.user_b = Users.objects.create(user='user_b', password='pass')
        self.user_c = Users.objects.create(user='user_c', password='pass')

        # 绑定角色
        UserAuthority.objects.create(user=self.user_a, authority=self.r1)  # A 有 R1
        UserAuthority.objects.create(user=self.user_b, authority=self.r2)  # B 有 R2
        UserAuthority.objects.create(user=self.user_c, authority=self.r3)  # C 有 R3

    def test_get_data_scope_authority_ids_recursive(self):
        """测试递归获取 data_authority 链"""
        ids = DataScopePermission.get_data_scope_authority_ids(self.user_a.id)
        self.assertEqual(ids, {1, 2})

    def test_get_data_scope_authority_ids_single(self):
        """测试无 data_authority 的角色"""
        ids = DataScopePermission.get_data_scope_authority_ids(self.user_b.id)
        self.assertEqual(ids, {2})

    def test_get_data_scope_user_ids(self):
        """测试获取数据权限范围内的用户"""
        # user_a 的权限范围包含 R1 和 R2，对应 user_a 和 user_b
        user_ids = DataScopePermission.get_data_scope_user_ids(self.user_a.id)
        self.assertIn(self.user_a.id, user_ids)
        self.assertIn(self.user_b.id, user_ids)
        self.assertNotIn(self.user_c.id, user_ids)

    def test_filter_queryset(self):
        """测试 queryset 数据权限过滤"""
        Cluster.objects.create(name='c_a', created_by=self.user_a)
        Cluster.objects.create(name='c_b', created_by=self.user_b)
        Cluster.objects.create(name='c_c', created_by=self.user_c)

        queryset = Cluster.objects.all()
        filtered = DataScopePermission.filter_queryset(queryset, self.user_a.id)
        names = set(filtered.values_list('name', flat=True))
        self.assertEqual(names, {'c_a', 'c_b'})

    def test_super_admin_skip_filter(self):
        """测试超级管理员跳过数据权限过滤"""
        admin_role = Authority.objects.create(authority_id=888, authority_name='超级管理员')
        admin = Users.objects.create(user='admin', password='pass')
        UserAuthority.objects.create(user=admin, authority=admin_role)

        Cluster.objects.create(name='c_x', created_by=self.user_a)

        queryset = Cluster.objects.all()
        filtered = DataScopePermission.filter_queryset(queryset, admin.id)
        self.assertEqual(filtered.count(), 1)


class DataScopeHostViewSetTest(APITestCase):
    """HostViewSet 数据权限集成测试"""

    def setUp(self):
        self.r1 = Authority.objects.create(authority_id=10, authority_name='R10')
        self.r2 = Authority.objects.create(authority_id=11, authority_name='R11')
        self.r1.data_authority = self.r2
        self.r1.save()

        # 普通管理员角色（用于通过 IsAdmin 权限校验）
        self.admin_role = Authority.objects.create(authority_id=889, authority_name='管理员')

        self.user_a = Users.objects.create(user='va', password='pass')
        self.user_b = Users.objects.create(user='vb', password='pass')
        # 同时拥有管理员角色 + 数据权限角色
        UserAuthority.objects.create(user=self.user_a, authority=self.admin_role)
        UserAuthority.objects.create(user=self.user_a, authority=self.r1)
        UserAuthority.objects.create(user=self.user_b, authority=self.admin_role)
        UserAuthority.objects.create(user=self.user_b, authority=self.r2)

        # user_a 创建主机
        Host.objects.create(hostname='host_a', ip_address='10.0.0.1', created_by=self.user_a)
        # user_b 创建主机
        Host.objects.create(hostname='host_b', ip_address='10.0.0.2', created_by=self.user_b)

    def test_list_hosts_data_scope(self):
        """user_a 只能看到自己和 data_authority 范围内的主机"""
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get('/api/hosts/')
        self.assertEqual(response.status_code, 200)
        results = response.data['data'].get('results', [])
        hostnames = {h['hostname'] for h in results}
        self.assertEqual(hostnames, {'host_a', 'host_b'})

    def test_list_hosts_shared_admin(self):
        """user_b 因共享管理员角色也能看到 host_a"""
        refresh = RefreshToken.for_user(self.user_b)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get('/api/hosts/')
        self.assertEqual(response.status_code, 200)
        results = response.data['data'].get('results', [])
        hostnames = {h['hostname'] for h in results}
        # user_a 和 user_b 共享管理员角色 889，因此彼此数据可见
        self.assertEqual(hostnames, {'host_a', 'host_b'})
