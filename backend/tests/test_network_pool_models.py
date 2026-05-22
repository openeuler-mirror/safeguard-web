"""LBPool 模型测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool


class LBPoolModelTest(TestCase):
    """LBPool 模型测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80
        )

    def test_create_pool(self):
        """测试创建后端池"""
        pool = LBPool.objects.create(
            name='TestPool',
            loadbalancer=self.lb,
            protocol='tcp',
            description='测试后端池'
        )
        self.assertEqual(pool.name, 'TestPool')
        self.assertEqual(pool.loadbalancer, self.lb)
        self.assertEqual(pool.protocol, 'tcp')
        self.assertEqual(pool.description, '测试后端池')

    def test_pool_str(self):
        """测试后端池字符串表示"""
        pool = LBPool(
            name='MyPool',
            protocol='http'
        )
        self.assertEqual(str(pool), 'MyPool - http')

    def test_pool_default_description(self):
        """测试后端池默认描述"""
        pool = LBPool.objects.create(
            name='DefaultDescPool',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        self.assertEqual(pool.description, '')

    def test_pool_protocol_choices(self):
        """测试后端池协议选项"""
        protocols = ['tcp', 'http', 'https']
        for i, protocol in enumerate(protocols):
            pool = LBPool.objects.create(
                name=f'Pool-{protocol}',
                loadbalancer=self.lb,
                protocol=protocol
            )
            self.assertEqual(pool.protocol, protocol)

    def test_pool_lb_relation(self):
        """测试后端池与负载均衡器的关系"""
        pool1 = LBPool.objects.create(
            name='Pool1',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        pool2 = LBPool.objects.create(
            name='Pool2',
            loadbalancer=self.lb,
            protocol='http'
        )
        self.assertEqual(self.lb.lbpool_set.count(), 2)
        self.assertIn(pool1, self.lb.lbpool_set.all())
        self.assertIn(pool2, self.lb.lbpool_set.all())

    def test_pool_cascade_delete(self):
        """测试删除负载均衡器时后端池也被删除"""
        pool = LBPool.objects.create(
            name='CascadePool',
            loadbalancer=self.lb,
            protocol='tcp'
        )
        pool_id = pool.id
        self.lb.delete()
        self.assertFalse(LBPool.objects.filter(id=pool_id).exists())

    def test_pool_ordering(self):
        """测试后端池按创建时间倒序"""
        pool1 = LBPool.objects.create(name='Pool1', loadbalancer=self.lb, protocol='tcp')
        pool2 = LBPool.objects.create(name='Pool2', loadbalancer=self.lb, protocol='http')
        pools = list(LBPool.objects.all())
        self.assertEqual(pools[0], pool2)
        self.assertEqual(pools[1], pool1)
