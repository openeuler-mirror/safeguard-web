from rest_framework import serializers
from backend.models.host import Cluster


class ClusterSerializer(serializers.ModelSerializer):
    """集群序列化器"""
    host_count = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ['id', 'name', 'description', 'vcenter_id', 'host_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_host_count(self, obj):
        return obj.host_set.count()


class ClusterCreateSerializer(serializers.ModelSerializer):
    """集群创建序列化器"""
    class Meta:
        model = Cluster
        fields = ['name', 'description', 'vcenter_id']


class ClusterUpdateSerializer(serializers.ModelSerializer):
    """集群更新序列化器"""
    class Meta:
        model = Cluster
        fields = ['name', 'description', 'vcenter_id']