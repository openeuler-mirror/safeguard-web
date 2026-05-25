"""LBHealthMonitor 模型测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBHealthMonitor


class LBHealthMonitorModelTest(TestCase):
    """LBHealthMonitor 模型测试"""

    def setUp(self):
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

    def test_create_health_monitor(self):
        """测试创建健康检查"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=10,
            timeout=5,
            retry=3,
            description='TCP健康检查'
        )
        self.assertEqual(monitor.pool, self.pool)
        self.assertEqual(monitor.monitor_type, 'tcp')
        self.assertEqual(monitor.interval, 10)
        self.assertEqual(monitor.timeout, 5)
        self.assertEqual(monitor.retry, 3)
        self.assertEqual(monitor.description, 'TCP健康检查')

    def test_health_monitor_str(self):
        """测试健康检查字符串表示"""
        monitor = LBHealthMonitor(
            pool=self.pool,
            monitor_type='http'
        )
        self.assertEqual(str(monitor), 'Monitor for TestPool - http')

    def test_health_monitor_default_interval(self):
        """测试健康检查默认间隔"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp'
        )
        self.assertEqual(monitor.interval, 5)

    def test_health_monitor_default_timeout(self):
        """测试健康检查默认超时"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp'
        )
        self.assertEqual(monitor.timeout, 3)

    def test_health_monitor_default_retry(self):
        """测试健康检查默认重试次数"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp'
        )
        self.assertEqual(monitor.retry, 3)

    def test_health_monitor_default_description(self):
        """测试健康检查默认描述"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp'
        )
        self.assertEqual(monitor.description, '')

    def test_health_monitor_type_choices(self):
        """测试健康检查类型选项"""
        types = ['tcp', 'http', 'ping']
        for i, monitor_type in enumerate(types):
            # 每个类型需要新的pool，因为 OneToOne
            pool = LBPool.objects.create(
                name=f'Pool-{monitor_type}',
                loadbalancer=self.lb,
                protocol='tcp'
            )
            monitor = LBHealthMonitor.objects.create(
                pool=pool,
                monitor_type=monitor_type
            )
            self.assertEqual(monitor.monitor_type, monitor_type)

    def test_health_monitor_pool_one_to_one(self):
        """测试健康检查与后端池一对一关系"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=10,
            timeout=5,
            retry=3
        )
        self.assertEqual(self.pool.lbhealthmonitor, monitor)

    def test_health_monitor_cascade_delete(self):
        """测试删除后端池时健康检查也被删除"""
        monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp'
        )
        monitor_id = monitor.id
        self.pool.delete()
        self.assertFalse(LBHealthMonitor.objects.filter(id=monitor_id).exists())

    def test_health_monitor_ordering(self):
        """测试健康检查按创建时间倒序"""
        pool1 = LBPool.objects.create(name='Pool1', loadbalancer=self.lb, protocol='tcp')
        pool2 = LBPool.objects.create(name='Pool2', loadbalancer=self.lb, protocol='http')
        monitor1 = LBHealthMonitor.objects.create(pool=pool1, monitor_type='tcp')
        monitor2 = LBHealthMonitor.objects.create(pool=pool2, monitor_type='http')
        monitors = list(LBHealthMonitor.objects.all())
        self.assertEqual(monitors[0], monitor2)
        self.assertEqual(monitors[1], monitor1)