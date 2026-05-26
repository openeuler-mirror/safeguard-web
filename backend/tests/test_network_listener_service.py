"""ListenerService 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBListener
from backend.services.network import ListenerService


class ListenerServiceTest(TestCase):
    """ListenerService 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active'
        )
        self.listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80,
            name='TestListener',
            description='Test Listener'
        )

    def test_list_listeners(self):
        """测试获取监听器列表"""
        result = ListenerService.list_listeners()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestListener')

    def test_list_listeners_with_pagination(self):
        """测试监听器列表分页"""
        for i in range(15):
            LBListener.objects.create(
                loadbalancer=self.lb,
                protocol='http',
                port=8080 + i,
                name=f'PaginatedListener{i}'
            )
        result = ListenerService.list_listeners(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_listeners_with_filter(self):
        """测试监听器列表过滤"""
        LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='http',
            port=9090,
            name='HTTPListener'
        )
        result = ListenerService.list_listeners(filters={'protocol': 'http'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'HTTPListener')

    def test_list_listeners_filter_by_lb(self):
        """测试按负载均衡器过滤监听器"""
        another_lb = LoadBalancer.objects.create(
            name='AnotherLB',
            vip_address='192.168.2.100',
            port=80
        )
        LBListener.objects.create(
            loadbalancer=another_lb,
            protocol='tcp',
            port=8888,
            name='AnotherListener'
        )
        result = ListenerService.list_listeners(filters={'loadbalancer': self.lb.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestListener')

    def test_get_listener(self):
        """测试获取监听器详情"""
        listener = ListenerService.get_listener(self.listener.id)
        self.assertIsNotNone(listener)
        self.assertEqual(listener.name, 'TestListener')
        self.assertEqual(listener.protocol, 'tcp')

    def test_get_listener_not_found(self):
        """测试获取不存在的监听器"""
        listener = ListenerService.get_listener(9999)
        self.assertIsNone(listener)

    def test_create_listener(self):
        """测试创建监听器"""
        data = {
            'protocol': 'http',
            'port': 8080,
            'name': 'NewListener',
            'description': 'New Listener'
        }
        listener = ListenerService.create_listener(self.lb.id, data)
        self.assertIsNotNone(listener)
        self.assertEqual(listener.name, 'NewListener')
        self.assertEqual(listener.protocol, 'http')
        self.assertEqual(listener.port, 8080)

    def test_create_listener_lb_not_found(self):
        """测试为不存在的负载均衡器创建监听器"""
        data = {'protocol': 'tcp', 'port': 80}
        listener = ListenerService.create_listener(9999, data)
        self.assertIsNone(listener)

    def test_update_listener(self):
        """测试更新监听器"""
        data = {'name': 'UpdatedListener', 'protocol': 'https', 'port': 8443}
        listener = ListenerService.update_listener(self.listener.id, data)
        self.assertEqual(listener.name, 'UpdatedListener')
        self.assertEqual(listener.protocol, 'https')
        self.assertEqual(listener.port, 8443)

    def test_update_listener_partial(self):
        """测试部分更新监听器"""
        data = {'port': 9999}
        listener = ListenerService.update_listener(self.listener.id, data)
        self.assertEqual(listener.name, 'TestListener')  # 名称不变
        self.assertEqual(listener.port, 9999)

    def test_update_listener_not_found(self):
        """测试更新不存在的监听器"""
        result = ListenerService.update_listener(9999, {'name': 'Test'})
        self.assertIsNone(result)

    def test_delete_listener(self):
        """测试删除监听器"""
        result = ListenerService.delete_listener(self.listener.id)
        self.assertTrue(result)
        self.assertFalse(LBListener.objects.filter(id=self.listener.id).exists())

    def test_delete_listener_not_found(self):
        """测试删除不存在的监听器"""
        result = ListenerService.delete_listener(9999)
        self.assertFalse(result)