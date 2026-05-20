"""后端池和池成员服务"""
from typing import Optional, List
from backend.models.network import LBPool, LBMember, LoadBalancer


class PoolService:
    """后端池服务"""

    @staticmethod
    def list_pools(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取后端池列表（支持分页和过滤）"""
        queryset = LBPool.objects.select_related('loadbalancer').all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_pool(pool_id: int) -> Optional[LBPool]:
        """获取后端池详情"""
        try:
            return LBPool.objects.select_related('loadbalancer').get(pk=pool_id)
        except LBPool.DoesNotExist:
            return None

    @staticmethod
    def create_pool(lb_id: int, data: dict) -> Optional[LBPool]:
        """创建后端池"""
        try:
            lb = LoadBalancer.objects.get(pk=lb_id)
        except LoadBalancer.DoesNotExist:
            return None

        pool = LBPool.objects.create(
            loadbalancer=lb,
            name=data.get('name'),
            protocol=data.get('protocol'),
            description=data.get('description', ''),
        )
        return pool

    @staticmethod
    def update_pool(pool_id: int, data: dict) -> Optional[LBPool]:
        """更新后端池"""
        try:
            pool = LBPool.objects.get(pk=pool_id)
            if 'name' in data:
                pool.name = data['name']
            if 'protocol' in data:
                pool.protocol = data['protocol']
            if 'description' in data:
                pool.description = data['description']
            pool.save()
            return pool
        except LBPool.DoesNotExist:
            return None

    @staticmethod
    def delete_pool(pool_id: int) -> bool:
        """删除后端池"""
        try:
            pool = LBPool.objects.get(pk=pool_id)
            pool.delete()
            return True
        except LBPool.DoesNotExist:
            return False

    @staticmethod
    def get_members(pool_id: int) -> List[LBMember]:
        """获取后端池的成员列表"""
        try:
            pool = LBPool.objects.get(pk=pool_id)
            return list(pool.members.all())
        except LBPool.DoesNotExist:
            return []


class MemberService:
    """池成员服务"""

    @staticmethod
    def list_members(filters: dict = None, page: int = 1, page_size: int = 10):
        """获取池成员列表（支持分页和过滤）"""
        queryset = LBMember.objects.select_related('pool').all()
        if filters:
            queryset = queryset.filter(**filters)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset[start:end])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_member(member_id: int) -> Optional[LBMember]:
        """获取池成员详情"""
        try:
            return LBMember.objects.select_related('pool').get(pk=member_id)
        except LBMember.DoesNotExist:
            return None

    @staticmethod
    def add_member(pool_id: int, data: dict) -> Optional[LBMember]:
        """添加池成员"""
        try:
            pool = LBPool.objects.get(pk=pool_id)
        except LBPool.DoesNotExist:
            return None

        member = LBMember.objects.create(
            pool=pool,
            address=data.get('address'),
            port=data.get('port'),
            weight=data.get('weight', 1),
            is_enabled=data.get('is_enabled', True),
            description=data.get('description', ''),
        )
        return member

    @staticmethod
    def update_member(member_id: int, data: dict) -> Optional[LBMember]:
        """更新池成员"""
        try:
            member = LBMember.objects.get(pk=member_id)
            if 'address' in data:
                member.address = data['address']
            if 'port' in data:
                member.port = data['port']
            if 'weight' in data:
                member.weight = data['weight']
            if 'is_enabled' in data:
                member.is_enabled = data['is_enabled']
            if 'description' in data:
                member.description = data['description']
            member.save()
            return member
        except LBMember.DoesNotExist:
            return None

    @staticmethod
    def remove_member(member_id: int) -> bool:
        """移除池成员"""
        try:
            member = LBMember.objects.get(pk=member_id)
            member.delete()
            return True
        except LBMember.DoesNotExist:
            return False