"""Redis客户端配置，支持本地Mock模式和线上Redis模式"""
import time

from safeguard_web.settings import IS_LOCAL, REDIS_HOST, REDIS_DB, REDIS_PASSWORD, REDIS_PORT


if IS_LOCAL:

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


__all__ = ['redis_client', 'MockRedis']
