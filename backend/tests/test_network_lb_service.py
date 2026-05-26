"""LBService 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBListener
from backend.services.network import LBService


class LBServiceTest(TestCase):
    """LBService 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80,
            algorithm='round_robin',
            status='active',
            description='Test LoadBalancer'
        )

    def test_list_lbs(self):
        """测试获取负载均衡器列表"""
        result = LBService.list_lbs()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestLB')

    def test_list_lbs_with_pagination(self):
        """测试负载均衡器列表分页"""
        for i in range(15):
            LoadBalancer.objects.create(
                name=f'PaginatedLB{i}',
                vip_address=f'192.168.1.{i+10}',
                port=80,
                algorithm='round_robin'
            )
        result = LBService.list_lbs(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_lbs_with_filter(self):
        """测试负载均衡器列表过滤"""
        LoadBalancer.objects.create(
            name='FilterLB',
            vip_address='192.168.2.100',
            port=8080,
            algorithm='least_conn',
            status='inactive'
        )
        result = LBService.list_lbs(filters={'algorithm': 'least_conn'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'FilterLB')

    def test_get_lb(self):
        """测试获取负载均衡器详情"""
        lb = LBService.get_lb(self.lb.id)
        self.assertIsNotNone(lb)
        self.assertEqual(lb.name, 'TestLB')
        self.assertEqual(lb.vip_address, '192.168.1.100')

    def test_get_lb_not_found(self):
        """测试获取不存在的负载均衡器"""
        lb = LBService.get_lb(9999)
        self.assertIsNone(lb)

    def test_create_lb(self):
        """测试创建负载均衡器"""
        data = {
            'name': 'NewLB',
            'vip_address': '192.168.1.200',
            'port': 8080,
            'algorithm': 'least_conn',
            'status': 'active',
            'description': 'New LoadBalancer'
        }
        lb = LBService.create_lb(data)
        self.assertEqual(lb.name, 'NewLB')
        self.assertEqual(lb.vip_address, '192.168.1.200')
        self.assertEqual(lb.algorithm, 'least_conn')

    def test_create_lb_with_defaults(self):
        """测试创建负载均衡器使用默认值"""
        data = {
            'name': 'DefaultLB',
            'vip_address': '192.168.1.50'
        }
        lb = LBService.create_lb(data)
        self.assertEqual(lb.port, 80)
        self.assertEqual(lb.algorithm, 'round_robin')
        self.assertEqual(lb.status, 'active')

    def test_update_lb(self):
        """测试更新负载均衡器"""
        data = {'name': 'UpdatedLB', 'algorithm': 'source', 'description': 'Updated'}
        lb = LBService.update_lb(self.lb.id, data)
        self.assertEqual(lb.name, 'UpdatedLB')
        self.assertEqual(lb.algorithm, 'source')
        self.assertEqual(lb.description, 'Updated')

    def test_update_lb_partial(self):
        """测试部分更新负载均衡器"""
        data = {'status': 'inactive'}
        lb = LBService.update_lb(self.lb.id, data)
        self.assertEqual(lb.name, 'TestLB')  # 名称不变
        self.assertEqual(lb.status, 'inactive')

    def test_update_lb_not_found(self):
        """测试更新不存在的负载均衡器"""
        result = LBService.update_lb(9999, {'Name': 'Test'})
        self.assertIsNone(result)

    def test_delete_lb(self):
        """测试删除负载均衡器"""
        result = LBService.delete_lb(self.lb.id)
        self.assertTrue(result)
        self.assertFalse(LoadBalancer.objects.filter(id=self.lb.id).exists())

    def test_delete_lb_not_found(self):
        """测试删除不存在的负载均衡器"""
        result = LBService.delete_lb(9999)
        self.assertFalse(result)

    def test_get_listeners(self):
        """测试获取负载均衡器的监听器列表"""
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
        listeners = LBService.get_listeners(self.lb.id)
        self.assertEqual(len(listeners), 2)

    def test_get_listeners_empty(self):
        """测试获取没有监听器的负载均衡器"""
        listeners = LBService.get_listeners(self.lb.id)
        self.assertEqual(len(listeners), 0)

    def test_get_listeners_lb_not_found(self):
        """测试获取不存在负载均衡器的监听器列表"""
        listeners = LBService.get_listeners(9999)
        self.assertEqual(listeners, [])