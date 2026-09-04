from typing import Any

import ujson
from redis.asyncio import Redis

from shared.cache.base.backend import BaseBackend
from shared.config import config


redis = Redis.from_url(config.REDIS_URL.unicode_string())


class RedisBackend(BaseBackend):
    async def get(self, key: str) -> Any:
        result = await redis.get(key)

        if result is None:
            return None

        if isinstance(result, bytes):
            payload = result.decode("utf-8")
        else:
            payload = result

        return ujson.loads(payload)

    async def set(
        self,
        response: Any,
        key: str,
        ttl: int = 60,
    ) -> None:
        try:
            serialized_data = ujson.dumps(response)
            await redis.set(
                name=key,
                value=serialized_data,
                ex=ttl,
            )
        except (TypeError, ValueError):
            # داده‌ی غیرقابل تبدیل به JSON در کش ذخیره نمی‌شود.
            return

    async def delete_startswith(self, value: str) -> None:
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)