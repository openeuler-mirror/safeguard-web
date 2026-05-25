"""LBMember 模型测试"""
from django.test import TestCase
from backend.models.network import LoadBalancer, LBPool, LBMember


class LBMemberModelTest(TestCase):
    """LBMember 模型测试"""

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

    def test_create_member(self):
        """测试创建池成员"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.1',
            port=8080,
            weight=3,
            is_enabled=True,
            description='后端服务器1'
        )
        self.assertEqual(member.pool, self.pool)
        self.assertEqual(member.address, '10.0.0.1')
        self.assertEqual(member.port, 8080)
        self.assertEqual(member.weight, 3)
        self.assertEqual(member.is_enabled, True)
        self.assertEqual(member.description, '后端服务器1')

    def test_member_str(self):
        """测试池成员字符串表示"""
        member = LBMember(
            pool=self.pool,
            address='10.0.0.1',
            port=8080
        )
        self.assertEqual(str(member), '10.0.0.1:8080')

    def test_member_default_weight(self):
        """测试池成员默认权重"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.2',
            port=8080
        )
        self.assertEqual(member.weight, 1)

    def test_member_default_is_enabled(self):
        """测试池成员默认启用状态"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.3',
            port=8080
        )
        self.assertEqual(member.is_enabled, True)

    def test_member_default_description(self):
        """测试池成员默认描述"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.0.4',
            port=8080
        )
        self.assertEqual(member.description, '')

    def test_member_pool_relation(self):
        """测试池成员与后端池的关系"""
        member1 = LBMember.objects.create(
            pool=self.pool,
            address='10.0.1.1',
            port=80
        )
        member2 = LBMember.objects.create(
            pool=self.pool,
            address='10.0.1.2',
            port=80
        )
        self.assertEqual(self.pool.members.count(), 2)
        self.assertIn(member1, self.pool.members.all())
        self.assertIn(member2, self.pool.members.all())

    def test_member_cascade_delete(self):
        """测试删除后端池时池成员也被删除"""
        member = LBMember.objects.create(
            pool=self.pool,
            address='10.0.2.1',
            port=3306
        )
        member_id = member.id
        self.pool.delete()
        self.assertFalse(LBMember.objects.filter(id=member_id).exists())

    def test_member_ordering(self):
        """测试池成员按创建时间倒序"""
        member1 = LBMember.objects.create(
            pool=self.pool,
            address='10.0.3.1',
            port=80
        )
        member2 = LBMember.objects.create(
            pool=self.pool,
            address='10.0.3.2',
            port=80
        )
        members = list(LBMember.objects.all())
        self.assertEqual(members[0], member2)
        self.assertEqual(members[1], member1)