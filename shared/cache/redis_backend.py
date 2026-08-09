import ujson
from typing import Any
from redis.asyncio import Redis  # فرض بر استفاده از کتابخانه مدرن redis-py
from shared.cache.base.backend import BaseBackend
from shared.config import config

# پیشنهاد: connection pool را در جایی خارج از این فایل مدیریت کنید
redis = Redis.from_url(config.REDIS_URL.unicode_string())

class RedisBackend(BaseBackend):
    async def get(self, key: str) -> Any:
        result = await redis.get(key)
        if not result:
            return None
        return ujson.loads(result.decode("utf-8"))

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        # فقط دیتای قابل تبدیل به JSON را کش می‌کنیم
        try:
            serialized_data = ujson.dumps(response)
            await redis.set(name=key, value=serialized_data, ex=ttl)
        except (TypeError, ValueError) as e:
            # اینجا می‌توان لاگ کرد که آبجکت غیرقابل سریالایز است
            pass

    async def delete_startswith(self, value: str) -> None:
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)
