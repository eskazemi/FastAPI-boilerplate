from __future__ import annotations
import time
import uuid
from typing import Any

from starlette.types import (
    ASGIApp, 
    Message, 
    Receive, 
    Scope, 
    Send,
)
from structlog.contextvars import (
    bind_contextvars, 
    clear_contextvars,
)

from shared.config import config as settings
from shared.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        # فقط HTTP requestها لاگ می‌شوند.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = self._get_headers(scope)

        request_id = self._get_request_id(headers)
        method = scope.get("method", "")
        path = scope.get("path", "")

        query_string = scope.get("query_string", b"").decode(
            "utf-8",
            errors="replace",
        )

        client_ip = self._get_client_ip(
            scope=scope,
            headers=headers,
            settings=settings,
        )

        # پاک‌کردن context مربوط به request قبلی
        clear_contextvars()

        # اطلاعات مشترک برای تمام لاگ‌های این request
        bind_contextvars(
            request_id=request_id,
            http_method=method,
            http_path=path,
            http_query=query_string or None,
            client_ip=client_ip,
            user_agent=headers.get("user-agent"),
        )

        start_time = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, response_started

            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])

                response_headers = list(message.get("headers", []))

                # اگر X-Request-ID قبلاً وجود نداشت، آن را اضافه کن.
                has_request_id_header = any(
                    key.lower() == b"x-request-id"
                    for key, _ in response_headers
                )

                if not has_request_id_header:
                    response_headers.append(
                        (
                            b"x-request-id",
                            request_id.encode("utf-8"),
                        )
                    )

                updated_message: Message = {
                    **message,
                    "headers": response_headers,
                }

                await send(updated_message)
                return

            # پیام‌های دیگر مثل http.response.body
            # بدون تغییر ارسال می‌شوند.
            await send(message)

        try:
            await self.app(
                scope,
                receive,
                send_wrapper,
            )

            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            log_method = (
                logger.warning
                if status_code >= 400
                else logger.info
            )

            log_method(
                "http_request_completed",
                http_status_code=status_code,
                duration_ms=duration_ms,
            )

        except Exception:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.exception(
                "http_request_failed",
                http_status_code=status_code,
                duration_ms=duration_ms,
                response_started=response_started,
            )

            raise

        finally:
            # جلوگیری از باقی‌ماندن context برای request بعدی
            clear_contextvars()

    @staticmethod
    def _get_headers(scope: Scope) -> dict[str, str]:
        return {
            key.decode("latin-1").lower(): value.decode(
                "latin-1",
                errors="replace",
            )
            for key, value in scope.get("headers", [])
        }

    @staticmethod
    def _get_request_id(headers: dict[str, str]) -> str:
        request_id = headers.get("x-request-id")

        # جلوگیری از پذیرش Header بسیار طولانی
        if request_id and len(request_id) <= 128:
            return request_id

        return str(uuid.uuid4())

    @staticmethod
    def _get_client_ip(
        scope: Scope,
        headers: dict[str, str],
        settings: Any,
    ) -> str | None:
        # فقط در صورتی X-Forwarded-For را معتبر بدان
        # که Proxy جلوی سرویس مورد اعتماد باشد.
        if settings.TRUST_FORWARDED_HEADERS:
            forwarded_for = headers.get("x-forwarded-for")

            if forwarded_for:
                return forwarded_for.split(",")[0].strip()

        client = scope.get("client")

        if client:
            return str(client[0])

        return None
