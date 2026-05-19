"""LBMember 序列化器"""
from rest_framework import serializers
from backend.models.network import LBMember


class LBMemberSerializer(serializers.ModelSerializer):
    """池成员序列化器"""
    pool_name = serializers.CharField(source='pool.name', read_only=True)

    class Meta:
        model = LBMember
        fields = [
            'id', 'pool', 'pool_name', 'address', 'port',
            'weight', 'is_enabled', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LBMemberListSerializer(serializers.ModelSerializer):
    """池成员列表序列化器（简化字段）"""
    pool_name = serializers.CharField(source='pool.name', read_only=True)

    class Meta:
        model = LBMember
        fields = ['id', 'pool', 'pool_name', 'address', 'port', 'weight', 'is_enabled']


class LBMemberCreateSerializer(serializers.ModelSerializer):
    """池成员创建序列化器"""

    class Meta:
        model = LBMember
        fields = ['pool', 'address', 'port', 'weight', 'is_enabled', 'description']


class LBMemberUpdateSerializer(serializers.ModelSerializer):
    """池成员更新序列化器"""

    class Meta:
        model = LBMember
        fields = ['address', 'port', 'weight', 'is_enabled', 'description']