"""基于Redis用户信息的用户对象"""
from django.contrib.auth.hashers import make_password

from safeguard_web.settings import REDIS_USER_TTL
from backend.authentication.redis_client import redis_client


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


__all__ = ['RedisUser']
