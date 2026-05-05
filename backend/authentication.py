"""自定义JWT认证，支持Redis校验和Mock模式"""
from typing import Optional, Tuple

from django.conf import settings
from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token


def get_redis_client():
    """获取Redis客户端，测试模式下使用Mock"""
    use_mock = getattr(settings, 'USE_MOCK_REDIS', False)

    if use_mock:
        # 使用内存Mock替代Redis
        class MockRedis:
            _data = {}

            def get(self, key):
                return self._data.get(key)

            def set(self, key, value, ex=None):
                self._data[key] = value
                return True

            def delete(self, key):
                if key in self._data:
                    del self._data[key]
                return True

            def exists(self, key):
                return key in self._data

            def expire(self, key, timeout):
                return True

        return MockRedis()
    else:
        import redis
        return redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            password=getattr(settings, 'REDIS_PASSWORD', '') or None,
            decode_responses=True,
        )


class RedisJWTAuthentication(JWTAuthentication):
    """自定义JWT认证类，通过Redis校验用户状态"""

    def get_user(self, validated_token: Token):
        """
        从Redis获取用户状态，替代数据库查询
        """
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token无效，缺少user_id')

        r = get_redis_client()
        user_key = f"user:{user_id}"

        # 从Redis获取用户数据
        user_data = r.get(user_key)

        if user_data:
            import json
            user_info = json.loads(user_data)
        else:
            # Redis中没有用户数据，从数据库查询
            from backend.models import Users
            try:
                user = Users.objects.get(id=user_id)
                user_info = {
                    'id': user.id,
                    'uuid': str(user.uuid),
                    'user': user.user,
                    'nickname': user.nickname,
                    'enable': user.enable,
                    'password': user.password,
                }
            except Users.DoesNotExist:
                raise AuthenticationFailed('用户不存在')

        # 校验用户是否启用
        enable = user_info.get('enable', 1)
        if enable != 1:
            raise AuthenticationFailed('用户已被禁用')

        return RedisUser(user_info)


class RedisUser:
    """
    基于Redis用户信息的用户对象（非持久化模型）
    用于request.user，不支持写操作
    """

    def __init__(self, user_info: dict, redis_client=None):
        self.id = user_info['id']
        self.uuid = user_info.get('uuid')
        self.user = user_info['user']
        self.nickname = user_info.get('nickname', '系统用户')
        self.enable = user_info.get('enable', 1)
        self.password = user_info.get('password', '')
        self._is_active = self.enable == 1
        self._redis_client = redis_client

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_authenticated(self) -> bool:
        """DRF权限检查需要此属性"""
        return True

    def __str__(self):
        return self.user

    def set_password(self, raw_password):
        """支持密码设置（但不持久化，仅当前请求有效）"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def save(self):
        """持久化用户信息到Redis"""
        if self._redis_client is None:
            self._redis_client = get_redis_client()
        user_key = f"user:{self.id}"
        import json
        user_info = {
            'id': self.id,
            'uuid': str(self.uuid) if self.uuid else None,
            'user': self.user,
            'nickname': self.nickname,
            'enable': self.enable,
            'password': self.password,
        }
        self._redis_client.set(user_key, json.dumps(user_info))
