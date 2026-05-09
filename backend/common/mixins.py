"""
序列化器响应包装
确保 DRF 序列化器返回统一格式
"""
from rest_framework.serializers import Serializer
from backend.common.responses import api_response


class UnifiedSerializerMixin:
    """
    统一序列化器响应格式的 Mixin
    让序列化器的 to_representation 返回统一格式 {errno, errmsg, data}
    """

    def to_representation(self, instance):
        """将实例转换为统一响应格式"""
        ret = super().to_representation(instance)
        return api_response(errno=0, data=ret)


class ListUnifiedSerializerMixin:
    """
    列表序列化器响应包装 Mixin
    用于 list 端点，将结果包装为 {errno, errmsg, data: {results: [...]}}
    """

    def to_representation(self, instance):
        """将实例转换为统一响应格式"""
        ret = super().to_representation(instance)
        # list 时，返回的是 results 数组，需要包装
        if isinstance(ret, list):
            return api_response(errno=0, data={'results': ret})
        return api_response(errno=0, data=ret)
