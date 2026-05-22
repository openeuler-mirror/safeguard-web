"""LBMember 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.network import LoadBalancer, LBPool, LBMember


class LBMemberViewSetTest(APITestCase):
    """LBMemberViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_member',
            password='testpass123',
            nickname='测试用户Member'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80
        )
        self.pool = LBPool.objects.create(
            name='TestPool',
            loadbalancer=self.lb,
            protocol='tcp'
        )

    def test_list_members(self):
        """测试列出池成员"""
        LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.1',
            port=8080,
            weight=1
        )
        LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.2',
            port=8080,
            weight=2
        )
        response = self.client.get('/api/members/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_member(self):
        """测试创建池成员"""
        data = {
            'pool': self.pool.pk,
            'address': '10.0.1.100',
            'port': 3306,
            'weight': 3,
            'is_enabled': True,
            'description': '数据库服务器'
        }
        response = self.client.post('/api/members/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['address'], '10.0.1.100')
        self.assertEqual(response.data['data']['port'], 3306)
        self.assertEqual(response.data['data']['weight'], 3)

    def test_retrieve_member(self):
        """测试获取单个池成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.2.1',
            port=6379,
            weight=1
        )
        response = self.client.get(f'/api/members/{member.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['address'], '10.0.2.1')
        self.assertEqual(response.data['data']['port'], 6379)

    def test_update_member(self):
        """测试更新池成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.3.1',
            port=80,
            weight=1
        )
        data = {
            'pool': self.pool.pk,
            'address': '10.0.3.1',
            'port': 443,
            'weight': 5,
            'is_enabled': False
        }
        response = self.client.put(f'/api/members/{member.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['port'], 443)
        self.assertEqual(response.data['data']['weight'], 5)
        self.assertEqual(response.data['data']['is_enabled'], False)

    def test_partial_update_member(self):
        """测试部分更新池成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.4.1',
            port=80,
            weight=1,
            is_enabled=True
        )
        data = {'weight': 10, 'is_enabled': False}
        response = self.client.patch(f'/api/members/{member.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['weight'], 10)
        self.assertEqual(response.data['data']['is_enabled'], False)

    def test_delete_member(self):
        """测试删除池成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.5.1',
            port=5432,
            weight=1
        )
        response = self.client.delete(f'/api/members/{member.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(LBMember.objects.filter(pk=member.pk).exists())

    def test_delete_pool_cascade_members(self):
        """测试删除后端池级联删除成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.6.1',
            port=80,
            weight=1
        )
        member_pk = member.pk
        self.client.delete(f'/api/pools/{self.pool.pk}/')
        self.assertFalse(LBMember.objects.filter(pk=member_pk).exists())