"""LBPool 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.network import LoadBalancer, LBPool


class LBPoolViewSetTest(APITestCase):
    """LBPoolViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_pool',
            password='testpass123',
            nickname='测试用户Pool'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80
        )

    def test_list_pools(self):
        """测试列出后端池"""
        LBPool.objects.create(
            name='Pool1',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        LBPool.objects.create(
            name='Pool2',
            loadbalancer=self.lb,
            protocol='http'
        )
        response = self.client.get('/api/pools/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_pool(self):
        """测试创建后端池"""
        data = {
            'name': 'NewPool',
            'loadbalancer': self.lb.pk,
            'protocol': 'tcp',
            'description': '新建后端池'
        }
        response = self.client.post('/api/pools/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'NewPool')
        self.assertEqual(response.data['data']['protocol'], 'tcp')

    def test_retrieve_pool(self):
        """测试获取单个后端池"""
        pool = LBPool.objects.create(
            name='TestPool',
            loadbalancer=self.lb,
            protocol='http'
        )
        response = self.client.get(f'/api/pools/{pool.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'TestPool')
        self.assertEqual(response.data['data']['protocol'], 'http')

    def test_update_pool(self):
        """测试更新后端池"""
        pool = LBPool.objects.create(
            name='OriginalPool',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        data = {
            'name': 'UpdatedPool',
            'loadbalancer': self.lb.pk,
            'protocol': 'https'
        }
        response = self.client.put(f'/api/pools/{pool.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'UpdatedPool')
        self.assertEqual(response.data['data']['protocol'], 'https')

    def test_partial_update_pool(self):
        """测试部分更新后端池"""
        pool = LBPool.objects.create(
            name='OriginalPool',
            loadbalancer=self.lb,
            protocol='tcp',
            description='原始描述'
        )
        data = {'description': '新描述'}
        response = self.client.patch(f'/api/pools/{pool.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['description'], '新描述')

    def test_delete_pool(self):
        """测试删除后端池"""
        pool = LBPool.objects.create(
            name='ToDeletePool',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        response = self.client.delete(f'/api/pools/{pool.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(LBPool.objects.filter(pk=pool.pk).exists())