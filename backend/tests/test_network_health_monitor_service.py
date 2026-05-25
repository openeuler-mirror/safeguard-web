"""HealthMonitorService 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBHealthMonitor
from backend.services.network import HealthMonitorService


class HealthMonitorServiceTest(TestCase):
    """HealthMonitorService 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active'
        )
        self.pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='TestPool',
            protocol='tcp'
        )
        self.monitor = LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='tcp',
            interval=5,
            timeout=3,
            retry=3,
            description='Test Health Monitor'
        )

    def test_list_monitors(self):
        """测试获取健康检查列表"""
        result = HealthMonitorService.list_monitors()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].monitor_type, 'tcp')

    def test_list_monitors_with_pagination(self):
        """测试健康检查列表分页"""
        for i in range(15):
            another_pool = LBPool.objects.create(
                loadbalancer=self.lb,
                name=f'Pool{i}',
                protocol='tcp'
            )
            LBHealthMonitor.objects.create(
                pool=another_pool,
                monitor_type='http',
                interval=10,
                timeout=5,
                retry=3
            )
        result = HealthMonitorService.list_monitors(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_monitors_with_filter(self):
        """测试健康检查列表过滤"""
        LBHealthMonitor.objects.create(
            pool=self.pool,
            monitor_type='http',
            interval=10,
            timeout=5,
            retry=3
        )
        result = HealthMonitorService.list_monitors(filters={'monitor_type': 'http'})
        self.assertEqual(result['total'], 1)

    def test_list_monitors_filter_by_pool(self):
        """测试按后端池过滤健康检查"""
        another_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='AnotherPool',
            protocol='tcp'
        )
        LBHealthMonitor.objects.create(
            pool=another_pool,
            monitor_type='ping',
            interval=5,
            timeout=3,
            retry=3
        )
        result = HealthMonitorService.list_monitors(filters={'pool': self.pool.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].monitor_type, 'tcp')

    def test_get_monitor(self):
        """测试获取健康检查详情"""
        monitor = HealthMonitorService.get_monitor(self.monitor.id)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.monitor_type, 'tcp')
        self.assertEqual(monitor.interval, 5)
        self.assertEqual(monitor.timeout, 3)
        self.assertEqual(monitor.retry, 3)

    def test_get_monitor_not_found(self):
        """测试获取不存在的健康检查"""
        monitor = HealthMonitorService.get_monitor(9999)
        self.assertIsNone(monitor)

    def test_create_monitor(self):
        """测试创建健康检查"""
        new_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='NewPool',
            protocol='http'
        )
        data = {
            'monitor_type': 'http',
            'interval': 10,
            'timeout': 5,
            'retry': 3,
            'description': 'New Monitor'
        }
        monitor = HealthMonitorService.create_monitor(new_pool.id, data)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.monitor_type, 'http')
        self.assertEqual(monitor.interval, 10)
        self.assertEqual(monitor.timeout, 5)

    def test_create_monitor_pool_not_found(self):
        """测试为不存在的后端池创建健康检查"""
        data = {'monitor_type': 'tcp', 'interval': 5, 'timeout': 3, 'retry': 3}
        monitor = HealthMonitorService.create_monitor(9999, data)
        self.assertIsNone(monitor)

    def test_update_monitor(self):
        """测试更新健康检查"""
        data = {
            'monitor_type': 'http',
            'interval': 20,
            'timeout': 10,
            'retry': 5,
            'description': 'Updated Monitor'
        }
        monitor = HealthMonitorService.update_monitor(self.monitor.id, data)
        self.assertEqual(monitor.monitor_type, 'http')
        self.assertEqual(monitor.interval, 20)
        self.assertEqual(monitor.timeout, 10)
        self.assertEqual(monitor.retry, 5)
        self.assertEqual(monitor.description, 'Updated Monitor')

    def test_update_monitor_partial(self):
        """测试部分更新健康检查"""
        data = {'interval': 15}
        monitor = HealthMonitorService.update_monitor(self.monitor.id, data)
        self.assertEqual(monitor.monitor_type, 'tcp')  # 类型不变
        self.assertEqual(monitor.interval, 15)

    def test_update_monitor_not_found(self):
        """测试更新不存在的健康检查"""
        result = HealthMonitorService.update_monitor(9999, {'interval': 10})
        self.assertIsNone(result)

    def test_delete_monitor(self):
        """测试删除健康检查"""
        result = HealthMonitorService.delete_monitor(self.monitor.id)
        self.assertTrue(result)
        self.assertFalse(LBHealthMonitor.objects.filter(id=self.monitor.id).exists())

    def test_delete_monitor_not_found(self):
        """测试删除不存在的健康检查"""
        result = HealthMonitorService.delete_monitor(9999)
        self.assertFalse(result)

    def test_get_monitor_by_pool(self):
        """测试根据后端池获取健康检查"""
        monitor = HealthMonitorService.get_monitor_by_pool(self.pool.id)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.monitor_type, 'tcp')

    def test_get_monitor_by_pool_not_found(self):
        """测试获取不存在后端池的健康检查"""
        monitor = HealthMonitorService.get_monitor_by_pool(9999)
        self.assertIsNone(monitor)

    def test_get_monitor_by_pool_no_monitor(self):
        """测试没有健康检查的后端池"""
        new_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='NoMonitorPool',
            protocol='tcp'
        )
        monitor = HealthMonitorService.get_monitor_by_pool(new_pool.id)
        self.assertIsNone(monitor)