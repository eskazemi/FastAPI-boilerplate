# shared/infrastructure/database/redis.py
from typing import Any, Optional
from uuid import UUID

from asyncpg.pgproto.pgproto import UUID as _UUID
from redis.asyncio import ConnectionPool
from redis.asyncio.client import Redis

from shared.config import config

# Pool سراسری - یک بار ساخته می‌شود و بین تمام instance های RedisManager مشترک است
redis_connection_pool = ConnectionPool.from_url(
    url=str(config.REDIS_URL), max_connections=100
)


class RedisManager:
    """
    Interface for dependency inversion of Dependency Injection. :)
    """

    def __init__(self, redis_url: Optional[str] = None) -> None:
        global redis_connection_pool

        if redis_url:
            # فقط وقتی url متفاوتی داده شده pool سراسری rebuild می‌شود
            redis_connection_pool = ConnectionPool.from_url(
                url=str(redis_url), max_connections=100
            )

        self.redis = Redis(connection_pool=redis_connection_pool)

    def serialize(self, data):
        if type(data) in [UUID, _UUID]:
            data = str(data)
        return data

    def deserialize(self, data) -> str:
        if type(data) is bytes:
            data = data.decode("utf-8")
        return data

    async def ttl(self, name) -> Any:
        name = self.serialize(name)
        result: int = await self.redis.ttl(name)
        return result

    async def get(self, name) -> Any:
        name = self.serialize(name)
        result: bytes | None | str = await self.redis.get(name)
        result = self.deserialize(result)
        return result

    async def set(self, name, value, ex: int, nx: bool = False) -> Any:
        name = self.serialize(name)
        value = self.serialize(value)
        result = await self.redis.set(name, value, ex, nx=nx)
        result = self.deserialize(result)
        return result

    async def delete(self, name) -> Any:
        name = self.serialize(name)
        result = await self.redis.delete(name)
        result = self.deserialize(result)
        return result

    async def flush_all(self) -> Any:
        result = await self.redis.flushall()
        return result

    def get_client(self) -> Redis:
        """دسترسی مستقیم به کلاینت اصلی ردیس برای عملیات‌های پیچیده"""
        return self.redis


def get_redis_db() -> RedisManager:
    return RedisManager()
