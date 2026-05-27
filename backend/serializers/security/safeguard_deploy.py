"""SafeguardDeploy 序列化器"""
from rest_framework import serializers
from backend.models.security import SafeguardDeploy


class SafeguardDeploySerializer(serializers.ModelSerializer):
    """Safeguard 部署序列化器"""
    description = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = SafeguardDeploy
        fields = [
            'id', 'name', 'target_hosts', 'safeguard_type', 'arch',
            'host', 'username', 'password', 'port', 'status',
            'result', 'error_message', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'result', 'error_message', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """自定义响应格式"""
        data = super().to_representation(instance)
        # 确保 result 为 dict 类型
        if isinstance(data.get('result'), list):
            data['result'] = {}
        return data


class SafeguardDeployListSerializer(serializers.ModelSerializer):
    """Safeguard 部署列表序列化器（简化字段）"""

    class Meta:
        model = SafeguardDeploy
        fields = ['id', 'name', 'safeguard_type', 'arch', 'host', 'status', 'created_at']


class SafeguardDeployCreateSerializer(serializers.ModelSerializer):
    """Safeguard 部署创建序列化器"""

    class Meta:
        model = SafeguardDeploy
        fields = [
            'name', 'target_hosts', 'safeguard_type', 'arch',
            'host', 'username', 'password', 'port', 'description'
        ]


class SafeguardDeployUpdateSerializer(serializers.ModelSerializer):
    """Safeguard 部署更新序列化器"""

    class Meta:
        model = SafeguardDeploy
        fields = [
            'name', 'target_hosts', 'safeguard_type', 'arch',
            'host', 'username', 'password', 'port', 'status', 'description'
        ]