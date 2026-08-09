import logging
from time import perf_counter
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("http.response")


class ResponseLoggerMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        logger_: logging.Logger | None = None,
    ) -> None:
        self.app = app
        self.logger = logger_ or logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = perf_counter()
        status_code: int | None = None

        async def logging_send(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message.get("status")

            await send(message)

        try:
            await self.app(scope, receive, logging_send)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000

            self.logger.exception(
                "HTTP request failed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": status_code or 500,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise
        finally:
            duration_ms = (perf_counter() - started_at) * 1000

            if status_code is not None:
                self.logger.info(
                    "HTTP request completed",
                    extra={
                        "method": scope.get("method"),
                        "path": scope.get("path"),
                        "status_code": status_code,
                        "duration_ms": round(duration_ms, 2),
                    },
                )
