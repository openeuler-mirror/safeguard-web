"""LBHealthMonitor 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.network import LoadBalancer, LBPool, LBHealthMonitor


class LBHealthMonitorViewSetTest(APITestCase):
    """LBHealthMonitorViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_monitor',
            password='testpass123',
            nickname='测试用户Monitor'
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

    def test_list_health_monitors(self):
        """测试列出健康检查"""
        LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3
        )
        another_pool = LBPool.objects.create(
            name='AnotherPool',
            loadbalancer=self.lb,
            protocol='http'
        )
        LBHealthMonitor.objects.create(
            pool=another_pool,
            monitor_type='http',
            interval=10,
            timeout=5,
            retry=2
        )
        response = self.client.get('/api/health-monitors/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_health_monitor(self):
        """测试创建健康检查"""
        another_pool = LBPool.objects.create(
            name='HTTPPool',
            loadbalancer=self.lb,
            protocol='http'
        )
        data = {
            'pool': another_pool.pk,
            'monitor_type': 'http',
            'interval': 10,
            'timeout': 5,
            'retry': 3,
            'description': 'HTTP健康检查'
        }
        response = self.client.post('/api/health-monitors/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['monitor_type'], 'http')
        self.assertEqual(response.data['data']['interval'], 10)
        self.assertEqual(response.data['data']['timeout'], 5)

    def test_retrieve_health_monitor(self):
        """测试获取单个健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3
        )
        response = self.client.get(f'/api/health-monitors/{monitor.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['monitor_type'], 'tcp')
        self.assertEqual(response.data['data']['interval'], 5)

    def test_update_health_monitor(self):
        """测试更新健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3
        )
        data = {
            'pool': self.pool.pk,
            'monitor_type': 'ping',
            'interval': 15,
            'timeout': 10,
            'retry': 5
        }
        response = self.client.put(f'/api/health-monitors/{monitor.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['monitor_type'], 'ping')
        self.assertEqual(response.data['data']['interval'], 15)
        self.assertEqual(response.data['data']['timeout'], 10)

    def test_partial_update_health_monitor(self):
        """测试部分更新健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3,
            description='原始描述'
        )
        data = {'interval': 20, 'description': '更新后的描述'}
        response = self.client.patch(f'/api/health-monitors/{monitor.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['interval'], 20)
        self.assertEqual(response.data['data']['description'], '更新后的描述')

    def test_delete_health_monitor(self):
        """测试删除健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3
        )
        response = self.client.delete(f'/api/health-monitors/{monitor.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(LBHealthMonitor.objects.filter(pk=monitor.pk).exists())

    def test_delete_pool_cascade_monitor(self):
        """测试删除后端池级联删除健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3
        )
        monitor_pk = monitor.pk
        self.client.delete(f'/api/pools/{self.pool.pk}/')
        self.assertFalse(LBHealthMonitor.objects.filter(pk=monitor_pk).exists())