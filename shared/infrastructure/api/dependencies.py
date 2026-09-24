
from shared.logging import get_logger
from fastapi import (
    Request, 
    Response, 
    HTTPException, 
)
from shared.services.rate_limit.ratelimiter import RateLimiterStore
from shared.utils.get_current_ip import get_client_ip
import time

class Duration:
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400

class Rate:
    def __init__(self, requests: int, duration: float):
        self.requests = requests
        self.duration = duration

class Limiter:
    def __init__(self, rate: Rate):
        self.rate = rate


class RateLimiter:
    def __init__(self, limiter: Limiter):
        """
        در زمان تعریف روت اجرا می‌شود.
        یک Store اختصاصی برای این روت می‌سازیم تا محدودیت‌های آن 
        با سایر روت‌ها تداخل (کاهش توکن اشتباه) نداشته باشد.
        """
        max_req = limiter.rate.requests
        interval_sec = limiter.rate.duration
        
        # مقداردهی کلاس Store شما بر اساس پارامترهای ورودی روت
        self.local_store = RateLimiterStore(
            max_tokens=max_req, 
            refill_rate=max_req, 
            interval=interval_sec
        )

    async def __call__(self, request: Request, response: Response):
        """
        در زمان دریافت درخواست (Request) اجرا می‌شود.
        """
        client_ip = get_client_ip(request=request)
        bucket = self.local_store.get_bucket(client_ip)

        if not bucket.allow_request():
            retry_after = bucket.get_reset_time() - time.time()
            headers = {
                "Retry-After": str(max(1, int(retry_after))),
                "X-RateLimit-Limit": str(bucket.max_tokens),
                "X-RateLimit-Remaining": str(bucket.get_remaining()),
                "X-RateLimit-Reset": str(int(bucket.get_reset_time())),
            }
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers=headers
            )

        response.headers["X-RateLimit-Limit"] = str(bucket.max_tokens)
        response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())
        response.headers["X-RateLimit-Reset"] = str(int(bucket.get_reset_time()))
