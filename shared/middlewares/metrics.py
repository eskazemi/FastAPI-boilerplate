import time
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    Counter, 
    Histogram,
)
from shared.config import config

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["app_name", "method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latency of FastAPI requests in seconds",
    ["endpoint", "method"],
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start_time

        path = request.url.path
        method = request.method

        REQUEST_COUNT.labels(
            app_name=config.APP_NAME,
            method=method,
            endpoint=path,
            http_status=str(response.status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=path,
            method=method,
        ).observe(latency)

        return response
