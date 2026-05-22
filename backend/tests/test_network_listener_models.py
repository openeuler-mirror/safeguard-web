"""LBListener 模型测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBListener


class LBListenerModelTest(TestCase):
    """LBListener 模型测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80
        )

    def test_create_listener(self):
        """测试创建监听器"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=3306,
            name='MySQL Listener',
            description='数据库监听'
        )
        self.assertEqual(listener.loadbalancer, self.lb)
        self.assertEqual(listener.protocol, 'tcp')
        self.assertEqual(listener.port, 3306)
        self.assertEqual(listener.name, 'MySQL Listener')
        self.assertEqual(listener.description, '数据库监听')

    def test_listener_str(self):
        """测试监听器字符串表示"""
        listener = LBListener(
            loadbalancer=self.lb,
            protocol='http',
            port=8080,
            name='HTTP Listener'
        )
        self.assertEqual(str(listener), 'HTTP Listener - http:8080')

    def test_listener_str_without_name(self):
        """测试无名称监听器字符串表示"""
        listener = LBListener(
            loadbalancer=self.lb,
            protocol='https',
            port=443,
            name=''
        )
        self.assertEqual(str(listener), 'Listener - https:443')

    def test_listener_default_name(self):
        """测试监听器默认名称"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=6379
        )
        self.assertEqual(listener.name, '')

    def test_listener_default_description(self):
        """测试监听器默认描述"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=6379
        )
        self.assertEqual(listener.description, '')

    def test_listener_protocol_choices(self):
        """测试监听器协议选项"""
        protocols = ['tcp', 'http', 'https']
        for i, protocol in enumerate(protocols):
            listener = LBListener.objects.create(
                loadbalancer=self.lb,
                protocol=protocol,
                port=8000 + i
            )
            self.assertEqual(listener.protocol, protocol)

    def test_listener_lb_relation(self):
        """测试监听器与负载均衡器的关系"""
        listener1 = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=80
        )
        listener2 = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='http',
            port=8080
        )
        self.assertEqual(self.lb.listeners.count(), 2)
        self.assertIn(listener1, self.lb.listeners.all())
        self.assertIn(listener2, self.lb.listeners.all())

    def test_listener_cascade_delete(self):
        """测试删除负载均衡器时监听器也被删除"""
        listener = LBListener.objects.create(
            loadbalancer=self.lb,
            protocol='tcp',
            port=3306
        )
        listener_id = listener.id
        self.lb.delete()
        self.assertFalse(LBListener.objects.filter(id=listener_id).exists())