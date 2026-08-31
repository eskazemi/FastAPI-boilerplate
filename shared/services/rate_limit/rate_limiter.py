# src/shared/infrastructure/services/rate_limiter.py
from redis.asyncio.client import Redis 
from shared.exceptions.base import TooManyRequestsException
import time

class RedisRateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check_limit(self, key: str, limit: int, window_seconds: int):
        full_key = f"rate_limit:{key}"
        now = time.time()
        
        # استفاده از Pipeline برای اتمیک بودن
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.zremrangebyscore(full_key, 0, now - window_seconds)
            await pipe.zadd(full_key, {str(now): now})
            await pipe.zcard(full_key)
            await pipe.expire(full_key, window_seconds)
            results = await pipe.execute()
            
            request_count = results[2] # نتیجه ZCARD

        if request_count > limit:
            raise TooManyRequestsException()
