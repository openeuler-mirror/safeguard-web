"""LoadBalancer 模型测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer


class LoadBalancerModelTest(TestCase):
    """LoadBalancer 模型测试"""

    def test_create_load_balancer(self):
        """测试创建负载均衡器"""
        lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.10',
            port=80,
            algorithm='round_robin',
            status='active',
            description='测试负载均衡器'
        )
        self.assertEqual(lb.name, 'TestLB')
        self.assertEqual(lb.vip_address, '192.168.1.10')
        self.assertEqual(lb.port, 80)
        self.assertEqual(lb.algorithm, 'round_robin')
        self.assertEqual(lb.status, 'active')
        self.assertEqual(lb.description, '测试负载均衡器')

    def test_load_balancer_str(self):
        """测试负载均衡器字符串表示"""
        lb = LoadBalancer(name='MyLB', vip_address='10.0.0.1')
        self.assertEqual(str(lb), 'MyLB - 10.0.0.1')

    def test_load_balancer_default_port(self):
        """测试负载均衡器默认端口"""
        lb = LoadBalancer.objects.create(
            name='DefaultPortLB',
            vip_address='192.168.1.20'
        )
        self.assertEqual(lb.port, 80)

    def test_load_balancer_default_algorithm(self):
        """测试负载均衡器默认算法"""
        lb = LoadBalancer.objects.create(
            name='DefaultAlgoLB',
            vip_address='192.168.1.30'
        )
        self.assertEqual(lb.algorithm, 'round_robin')

    def test_load_balancer_default_status(self):
        """测试负载均衡器默认状态"""
        lb = LoadBalancer.objects.create(
            name='DefaultStatusLB',
            vip_address='192.168.1.40'
        )
        self.assertEqual(lb.status, 'active')

    def test_load_balancer_default_description(self):
        """测试负载均衡器默认描述"""
        lb = LoadBalancer.objects.create(
            name='DefaultDescLB',
            vip_address='192.168.1.50'
        )
        self.assertEqual(lb.description, '')

    def test_load_balancer_algorithm_choices(self):
        """测试负载均衡器算法选项"""
        for algo_value, algo_label in LoadBalancer.ALGORITHM_CHOICES:
            lb = LoadBalancer.objects.create(
                name=f'LB-{algo_value}',
                vip_address=f'192.168.1.{10 + LoadBalancer.ALGORITHM_CHOICES.index((algo_value, algo_label))}',
                algorithm=algo_value
            )
            self.assertEqual(lb.algorithm, algo_value)

    def test_load_balancer_status_choices(self):
        """测试负载均衡器状态选项"""
        for status_value, status_label in LoadBalancer.STATUS_CHOICES:
            lb = LoadBalancer.objects.create(
                name=f'StatusLB-{status_value}',
                vip_address=f'192.168.2.{10 + LoadBalancer.STATUS_CHOICES.index((status_value, status_label))}',
                status=status_value
            )
            self.assertEqual(lb.status, status_value)

    def test_load_balancer_ordering(self):
        """测试负载均衡器按创建时间倒序"""
        lb1 = LoadBalancer.objects.create(name='LB1', vip_address='192.168.3.1')
        lb2 = LoadBalancer.objects.create(name='LB2', vip_address='192.168.3.2')
        lbs = list(LoadBalancer.objects.all())
        self.assertEqual(lbs[0], lb2)
        self.assertEqual(lbs[1], lb1)