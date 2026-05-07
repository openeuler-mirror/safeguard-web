"""Authentication模块，支持Redis校验和Mock模式"""
from backend.authentication.redis_client import redis_client
from backend.authentication.jwt import RedisJWTAuthentication
from backend.authentication.user import RedisUser

__all__ = [
    'redis_client',
    'RedisJWTAuthentication',
    'RedisUser',
]
