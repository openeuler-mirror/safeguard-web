"""LoadBalancer 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.network import LoadBalancer


class LoadBalancerViewSetTest(APITestCase):
    """LoadBalancerViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_lb',
            password='testpass123',
            nickname='测试用户LB'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_load_balancers(self):
        """测试列出负载均衡器"""
        LoadBalancer.objects.create(
            name='LB1',
            vip_address='192.168.1.10',
            port=80,
            algorithm='round_robin',
            status='active'
        )
        LoadBalancer.objects.create(
            name='LB2',
            vip_address='192.168.1.11',
            port=443,
            algorithm='least_conn',
            status='active'
        )
        response = self.client.get('/api/lbs/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_load_balancer(self):
        """测试创建负载均衡器"""
        data = {
            'name': 'NewLB',
            'vip_address': '192.168.1.100',
            'port': 8080,
            'algorithm': 'round_robin',
            'status': 'active',
            'description': '新建负载均衡器'
        }
        response = self.client.post('/api/lbs/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'NewLB')
        self.assertEqual(response.data['data']['vip_address'], '192.168.1.100')
        self.assertEqual(response.data['data']['port'], 8080)

    def test_retrieve_load_balancer(self):
        """测试获取单个负载均衡器"""
        lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.20',
            port=80,
            algorithm='source'
        )
        response = self.client.get(f'/api/lbs/{lb.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'TestLB')
        self.assertEqual(response.data['data']['vip_address'], '192.168.1.20')

    def test_update_load_balancer(self):
        """测试更新负载均衡器"""
        lb = LoadBalancer.objects.create(
            name='OriginalLB',
            vip_address='192.168.1.30',
            port=80
        )
        data = {
            'name': 'UpdatedLB',
            'vip_address': '192.168.1.30',
            'port': 443,
            'algorithm': 'least_conn',
            'status': 'inactive'
        }
        response = self.client.put(f'/api/lbs/{lb.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'UpdatedLB')
        self.assertEqual(response.data['data']['algorithm'], 'least_conn')

    def test_partial_update_load_balancer(self):
        """测试部分更新负载均衡器"""
        lb = LoadBalancer.objects.create(
            name='OriginalLB',
            vip_address='192.168.1.40',
            port=80,
            status='active'
        )
        data = {'status': 'inactive', 'description': '已停用'}
        response = self.client.patch(f'/api/lbs/{lb.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['status'], 'inactive')
        self.assertEqual(response.data['data']['description'], '已停用')

    def test_delete_load_balancer(self):
        """测试删除负载均衡器"""
        lb = LoadBalancer.objects.create(
            name='ToDeleteLB',
            vip_address='192.168.1.50'
        )
        response = self.client.delete(f'/api/lbs/{lb.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(LoadBalancer.objects.filter(pk=lb.pk).exists())