import time
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from shared.services.rate_limit.ratelimiter import RateLimiterStore

# ۲. ساختن نمونه (Instance) از کلاس و تعیین محدودیت‌ها
# در اینجا تعیین می‌کنیم: حداکثر ظرفیت 10 توکن، و هر 1 ثانیه 2 توکن شارژ شود
global_limiter_store = RateLimiterStore(max_tokens=10, refill_rate=2, interval=2.0)


# ۳. تعریف میدل‌ور
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter_store: RateLimiterStore):
        super().__init__(app)
        self.limiter_store = limiter_store

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # گرفتن سطل مربوط به این IP از همان نمونه‌ای که بیرون ساختیم
        bucket = self.limiter_store.get_bucket(client_ip)

        if not bucket.allow_request():
            retry_after = bucket.get_reset_time() - time.time()
            headers = {
                "Retry-After": str(max(1, int(retry_after))),
                "X-RateLimit-Limit": str(bucket.max_tokens),
                "X-RateLimit-Remaining": str(bucket.get_remaining()),
                "X-RateLimit-Reset": str(int(bucket.get_reset_time())),
            }
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
                headers=headers
            )

        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(bucket.max_tokens)
        response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())
        response.headers["X-RateLimit-Reset"] = str(int(bucket.get_reset_time()))
        
        return response