"""自定义JWT认证，支持Redis校验和Mock模式"""
from typing import Optional, Tuple

from django.conf import settings
from rest_framework import authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token
from safeguard_web.settings import IS_LOCAL, REDIS_HOST, REDIS_DB, REDIS_PASSWORD, REDIS_PORT, REDIS_USER_TTL


if IS_LOCAL:
    import time

    class MockRedis:
        """支持过期时间的内存Redis Mock"""

        class _KeyEntry:
            """统一保存键值和过期时间"""
            def __init__(self, value, expire_time=None):
                self.value = value
                self.expire_time = expire_time  # None表示永久

            def is_expired(self):
                return self.expire_time is not None and time.time() > self.expire_time

        _store = {}

        def get(self, key):
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._store[key]
                return None
            return entry.value

        def set(self, key, value, ex=None):
            expire_time = time.time() + ex if ex is not None else None
            self._store[key] = self._KeyEntry(value, expire_time)
            return True

        def delete(self, key):
            if key in self._store:
                del self._store[key]
            return True

        def exists(self, key):
            entry = self._store.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._store[key]
                return False
            return True

        def expire(self, key, timeout):
            entry = self._store.get(key)
            if entry is None:
                return False
            entry.expire_time = time.time() + timeout
            return True

        def ttl(self, key):
            """返回键的剩余生存时间（秒），-1表示永久，-2表示不存在或已过期"""
            entry = self._store.get(key)
            if entry is None:
                return -2
            if entry.expire_time is None:
                return -1
            remaining = entry.expire_time - time.time()
            if remaining <= 0:
                del self._store[key]
                return -2
            return int(remaining)

    redis_client = MockRedis()
else:
    import redis
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
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

        user_key = f"user:{user_id}"

        # 从Redis获取用户数据
        user_data = redis_client.get(user_key)

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

    def save(self, ex=None):
        """持久化用户信息到Redis（默认使用配置的过期时间）"""
        if ex is None:
            ex = REDIS_USER_TTL
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
        redis_client.set(user_key, json.dumps(user_info), ex=ex)
