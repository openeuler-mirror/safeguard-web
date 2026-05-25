"""LBListener 视图集测试"""
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Users, Authority, UserAuthority
from backend.models.network import LoadBalancer, LBListener


class LBListenerViewSetTest(APITestCase):
    """LBListenerViewSet 测试"""

    def setUp(self):
        """创建测试用户并获取JWT token"""
        self.admin_auth = Authority.objects.create(
            authority_id=888,
            authority_name='超级管理员'
        )
        self.user = Users.objects.create(
            user='testuser_listener',
            password='testpass123',
            nickname='测试用户Listener'
        )
        UserAuthority.objects.create(user=self.user, authority=self.admin_auth)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80
        )

    def test_list_listeners(self):
        """测试列出监听器"""
        LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80,
            name='Listener1'
        )
        LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='http',
            port=8080,
            name='Listener2'
        )
        response = self.client.get('/api/listeners/')
        self.assertEqual(response.data['errno'], 0)
        results = response.data['data']
        if isinstance(results, dict):
            results = results.get('results', [])
        self.assertEqual(len(results), 2)

    def test_create_listener(self):
        """测试创建监听器"""
        data = {
            'loadbalancer': self.lb.pk,
            'protocol': 'tcp',
            'port': 3306,
            'name': 'MySQL Listener',
            'description': '数据库监听'
        }
        response = self.client.post('/api/listeners/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['protocol'], 'tcp')
        self.assertEqual(response.data['data']['port'], 3306)
        self.assertEqual(response.data['data']['name'], 'MySQL Listener')

    def test_retrieve_listener(self):
        """测试获取单个监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='https',
            port=443,
            name='HTTPS Listener'
        )
        response = self.client.get(f'/api/listeners/{listener.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['protocol'], 'https')
        self.assertEqual(response.data['data']['port'], 443)

    def test_update_listener(self):
        """测试更新监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=8080,
            name='Original'
        )
        data = {
            'loadbalancer': self.lb.pk,
            'protocol': 'http',
            'port': 9090,
            'name': 'Updated'
        }
        response = self.client.put(f'/api/listeners/{listener.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['protocol'], 'http')
        self.assertEqual(response.data['data']['port'], 9090)
        self.assertEqual(response.data['data']['name'], 'Updated')

    def test_partial_update_listener(self):
        """测试部分更新监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80,
            name='Original'
        )
        data = {'name': 'Patched', 'description': '更新描述'}
        response = self.client.patch(f'/api/listeners/{listener.pk}/', data, format='json')
        self.assertEqual(response.data['errno'], 0)
        self.assertEqual(response.data['data']['name'], 'Patched')
        self.assertEqual(response.data['data']['description'], '更新描述')

    def test_delete_listener(self):
        """测试删除监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=6379,
            name='Redis Listener'
        )
        response = self.client.delete(f'/api/listeners/{listener.pk}/')
        self.assertEqual(response.data['errno'], 0)
        self.assertFalse(LBListener.objects.filter(pk=listener.pk).exists())

    def test_delete_listener_with_lb_cascade(self):
        """测试删除负载均衡器级联删除监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80
        )
        listener_pk = listener.pk
        self.client.delete(f'/api/lbs/{self.lb.pk}/')
        self.assertFalse(LBListener.objects.filter(pk=listener_pk).exists())