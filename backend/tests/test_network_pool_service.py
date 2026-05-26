"""PoolService 和 MemberService 测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBMember
from backend.services.network import PoolService, MemberService


class PoolServiceTest(TestCase):
    """PoolService 测试"""

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
            protocol='tcp',
            description='Test Pool'
        )

    def test_list_pools(self):
        """测试获取后端池列表"""
        result = PoolService.list_pools()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestPool')

    def test_list_pools_with_pagination(self):
        """测试后端池列表分页"""
        for i in range(15):
            LBPool.objects.create(
                loadbalancer=self.lb,
                name=f'PaginatedPool{i}',
                protocol='http'
            )
        result = PoolService.list_pools(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_pools_with_filter(self):
        """测试后端池列表过滤"""
        LBPool.objects.create(
            loadbalancer=self.lb,
            name='HTTPPool',
            protocol='http'
        )
        result = PoolService.list_pools(filters={'protocol': 'http'})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'HTTPPool')

    def test_list_pools_filter_by_lb(self):
        """测试按负载均衡器过滤后端池"""
        another_lb = LoadBalancer.objects.create(
            name='AnotherLB',
            vip_address='192.168.2.100',
            port=80
        )
        LBPool.objects.create(
            loadbalancer=another_lb,
            name='AnotherPool',
            protocol='tcp'
        )
        result = PoolService.list_pools(filters={'loadbalancer': self.lb.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].name, 'TestPool')

    def test_get_pool(self):
        """测试获取后端池详情"""
        pool = PoolService.get_pool(self.pool.id)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, 'TestPool')
        self.assertEqual(pool.protocol, 'tcp')

    def test_get_pool_not_found(self):
        """测试获取不存在的后端池"""
        pool = PoolService.get_pool(9999)
        self.assertIsNone(pool)

    def test_create_pool(self):
        """测试创建后端池"""
        data = {
            'name': 'NewPool',
            'protocol': 'http',
            'description': 'New Pool'
        }
        pool = PoolService.create_pool(self.lb.id, data)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, 'NewPool')
        self.assertEqual(pool.protocol, 'http')

    def test_create_pool_lb_not_found(self):
        """测试为不存在的负载均衡器创建后端池"""
        data = {'name': 'NewPool', 'protocol': 'tcp'}
        pool = PoolService.create_pool(9999, data)
        self.assertIsNone(pool)

    def test_update_pool(self):
        """测试更新后端池"""
        data = {'name': 'UpdatedPool', 'protocol': 'https', 'description': 'Updated'}
        pool = PoolService.update_pool(self.pool.id, data)
        self.assertEqual(pool.name, 'UpdatedPool')
        self.assertEqual(pool.protocol, 'https')
        self.assertEqual(pool.description, 'Updated')

    def test_update_pool_partial(self):
        """测试部分更新后端池"""
        data = {'description': 'Only description updated'}
        pool = PoolService.update_pool(self.pool.id, data)
        self.assertEqual(pool.name, 'TestPool')  # 名称不变
        self.assertEqual(pool.description, 'Only description updated')

    def test_update_pool_not_found(self):
        """测试更新不存在的后端池"""
        result = PoolService.update_pool(9999, {'name': 'Test'})
        self.assertIsNone(result)

    def test_delete_pool(self):
        """测试删除后端池"""
        result = PoolService.delete_pool(self.pool.id)
        self.assertTrue(result)
        self.assertFalse(LBPool.objects.filter(id=self.pool.id).exists())

    def test_delete_pool_not_found(self):
        """测试删除不存在的后端池"""
        result = PoolService.delete_pool(9999)
        self.assertFalse(result)

    def test_get_members(self):
        """测试获取后端池的成员列表"""
        LBMember.objects.create(
            pool=self.pool,
            address='192.168.1.10',
            port=8080,
            weight=1
        )
        LBMember.objects.create(
            pool=self.pool,
            address='192.168.1.11',
            port=8080,
            weight=2
        )
        members = PoolService.get_members(self.pool.id)
        self.assertEqual(len(members), 2)

    def test_get_members_empty(self):
        """测试获取没有成员的后端池"""
        members = PoolService.get_members(self.pool.id)
        self.assertEqual(len(members), 0)

    def test_get_members_pool_not_found(self):
        """测试获取不存在后端池的成员列表"""
        members = PoolService.get_members(9999)
        self.assertEqual(members, [])


class MemberServiceTest(TestCase):
    """MemberService 测试"""

    def setUp(self):
        self.lb = LoadBalancer.objects.create(
            name='TestLB',
            vip_address='192.168.1.100',
            port=80
        )
        self.pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='TestPool',
            protocol='tcp'
        )
        self.member = LBMember.objects.create(
            pool=self.pool,
            address='192.168.1.10',
            port=8080,
            weight=1,
            is_enabled=True,
            description='Test Member'
        )

    def test_list_members(self):
        """测试获取池成员列表"""
        result = MemberService.list_members()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].address, '192.168.1.10')

    def test_list_members_with_pagination(self):
        """测试池成员列表分页"""
        for i in range(15):
            LBMember.objects.create(
                pool=self.pool,
                address=f'192.168.1.{i+20}',
                port=8080,
                weight=1
            )
        result = MemberService.list_members(page=1, page_size=5)
        self.assertEqual(result['total'], 16)
        self.assertEqual(len(result['results']), 5)

    def test_list_members_with_filter(self):
        """测试池成员列表过滤"""
        LBMember.objects.create(
            pool=self.pool,
            address='192.168.2.10',
            port=9090,
            weight=2,
            is_enabled=False
        )
        result = MemberService.list_members(filters={'is_enabled': False})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].address, '192.168.2.10')

    def test_list_members_filter_by_pool(self):
        """测试按后端池过滤成员"""
        another_pool = LBPool.objects.create(
            loadbalancer=self.lb,
            name='AnotherPool',
            protocol='tcp'
        )
        LBMember.objects.create(
            pool=another_pool,
            address='192.168.3.10',
            port=8080
        )
        result = MemberService.list_members(filters={'pool': self.pool.id})
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['results'][0].address, '192.168.1.10')

    def test_get_member(self):
        """测试获取池成员详情"""
        member = MemberService.get_member(self.member.id)
        self.assertIsNotNone(member)
        self.assertEqual(member.address, '192.168.1.10')
        self.assertEqual(member.port, 8080)

    def test_get_member_not_found(self):
        """测试获取不存在的池成员"""
        member = MemberService.get_member(9999)
        self.assertIsNone(member)

    def test_add_member(self):
        """测试添加池成员"""
        data = {
            'address': '192.168.1.20',
            'port': 9090,
            'weight': 2,
            'is_enabled': True,
            'description': 'New Member'
        }
        member = MemberService.add_member(self.pool.id, data)
        self.assertIsNotNone(member)
        self.assertEqual(member.address, '192.168.1.20')
        self.assertEqual(member.weight, 2)

    def test_add_member_pool_not_found(self):
        """测试为不存在的后端池添加成员"""
        data = {'address': '192.168.1.20', 'port': 8080}
        member = MemberService.add_member(9999, data)
        self.assertIsNone(member)

    def test_update_member(self):
        """测试更新池成员"""
        data = {'address': '192.168.1.99', 'weight': 5, 'is_enabled': False}
        member = MemberService.update_member(self.member.id, data)
        self.assertEqual(member.address, '192.168.1.99')
        self.assertEqual(member.weight, 5)
        self.assertFalse(member.is_enabled)

    def test_update_member_partial(self):
        """测试部分更新池成员"""
        data = {'weight': 10}
        member = MemberService.update_member(self.member.id, data)
        self.assertEqual(member.address, '192.168.1.10')  # 地址不变
        self.assertEqual(member.weight, 10)

    def test_update_member_not_found(self):
        """测试更新不存在的池成员"""
        result = MemberService.update_member(9999, {'weight': 5})
        self.assertIsNone(result)

    def test_remove_member(self):
        """测试移除池成员"""
        result = MemberService.remove_member(self.member.id)
        self.assertTrue(result)
        self.assertFalse(LBMember.objects.filter(id=self.member.id).exists())

    def test_remove_member_not_found(self):
        """测试移除不存在的池成员"""
        result = MemberService.remove_member(9999)
        self.assertFalse(result)