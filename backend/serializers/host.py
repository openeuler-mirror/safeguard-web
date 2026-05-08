from rest_framework import serializers
from backend.models.host import Cluster, Host


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


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器（不返回密码）"""
    cluster_name = serializers.CharField(source='cluster.name', read_only=True)

    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'port', 'username',
            'cluster', 'cluster_name', 'status', 'os_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HostCreateSerializer(serializers.ModelSerializer):
    """主机创建序列化器"""
    class Meta:
        model = Host
        fields = ['hostname', 'ip_address', 'port', 'username', 'password', 'cluster', 'status', 'os_type']


class HostUpdateSerializer(serializers.ModelSerializer):
    """主机更新序列化器"""
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Host
        fields = ['hostname', 'port', 'username', 'password', 'cluster', 'status', 'os_type']

    def update(self, instance, validated_data):
        # 如果 password 为空，不更新密码字段
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = password
        instance.save()
        return instance


class HostListSerializer(serializers.ModelSerializer):
    """主机列表序列化器（简化字段）"""
    cluster_name = serializers.CharField(source='cluster.name', read_only=True)

    class Meta:
        model = Host
        fields = ['id', 'hostname', 'ip_address', 'port', 'cluster', 'cluster_name', 'status', 'os_type']