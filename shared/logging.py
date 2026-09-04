from __future__ import annotations
import logging
import sys
from collections.abc import Mapping
from typing import Any
import structlog
from structlog.types import EventDict, Processor

from shared.config import config


# مقدار ثابت برای جلوگیری از ساخت چندباره رشته در هر رخداد.
REDACTED_VALUE = "***REDACTED***"

# کلیدها به‌صورت lowercase تعریف شده‌اند تا مقایسه case-insensitive باشد.
SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "secret",
        "client_secret",
        "api_key",
        "apikey",
        "credit_card",
    }
)


def add_service_metadata(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    افزودن metadata ثابت سرویس به تمام رخدادهای لاگ.

    استفاده از setdefault باعث می‌شود اگر یک رخداد عمداً مقدار متفاوتی
    برای این فیلدها ارسال کرده باشد، مقدار آن بازنویسی نشود.
    """

    event_dict.setdefault("service", config.APP_NAME)
    event_dict.setdefault("service_version", config.APP_VERSION)
    event_dict.setdefault("environment", config.ENVIRONMENT)

    return event_dict


def redact_sensitive_data(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    حذف مقادیر حساس از ساختارهای تو‌در‌تو قبل از رندر نهایی لاگ.

    این processor دیکشنری‌ها و collectionهای متداول را به‌صورت recursive
    بررسی می‌کند. tuple و set به list تبدیل می‌شوند تا خروجی با JSON
    سازگار باشد.
    """

    def redact(value: Any) -> Any:
        if isinstance(value, Mapping):
            redacted_mapping: dict[Any, Any] = {}

            for key, item in value.items():
                normalized_key = str(key).strip().lower()

                if normalized_key in SENSITIVE_KEYS:
                    redacted_mapping[key] = REDACTED_VALUE
                else:
                    redacted_mapping[key] = redact(item)

            return redacted_mapping

        if isinstance(value, (list, tuple)):
            return [redact(item) for item in value]

        if isinstance(value, (set, frozenset)):
            # set مستقیماً توسط json.dumps قابل serialize شدن نیست.
            return [redact(item) for item in value]

        return value

    # EventDict در عمل یک mutable dict نیز dict اما خروجی redact نیز dict خواهد بود.
    redacted_event = redact(event_dict)

    if not isinstance(redacted_event, dict):
        # این حالت نباید رخ دهد، ولی قرارداد Processor را حفظ می‌کند.
        return event_dict

    return redacted_event


def configure_logging() -> None:
    """
    تنظیم یکپارچه logging استاندارد پایتون و Structlog.

    این تابع باید در ابتدای startup برنامه و قبل از ساخت loggerهای
    سراسری یا شروع پردازش requestها فراخوانی شود.
    """

    # این processorها هم برای رخدادهای Structlog و هم برای لاگ‌های تولیدشده
    # توسط کتابخانه‌هایی که از logging استاندارد استفاده می‌کنند اجرا می‌شوند.
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_service_metadata,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        redact_sensitive_data,
    ]

    # JSON برای محیط production و ارسال به Loki/Elasticsearch مناسب است.
    # ConsoleRenderer خروجی خواناتری برای توسعه محلی تولید می‌کند.
    renderer: Processor

    if config.LOG_JSON:
        renderer = structlog.processors.JSONRenderer(
            ensure_ascii=False,
        )
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stdout.isatty(),
        )

    # ProcessorFormatter نقطه اتصال logging استاندارد و Structlog است.
    # foreign_pre_chain فقط روی LogRecordهایی اجرا می‌شود که مستقیماً توسط
    # logging استاندارد، Uvicorn یا کتابخانه‌های دیگر تولید شده‌اند.
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # پاک‌کردن handlerهای قبلی، configure_logging را تا حد زیادی idempotent
    # می‌کند و جلوی تکراری‌شدن خطوط لاگ را در reload یا تست‌ها می‌گیرد.
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(config.LOG_LEVEL.upper())

    # warningهای صادرشده از ماژول warnings نیز وارد logging می‌شوند.
    logging.captureWarnings(True)

    # کاهش نویز کتابخانه‌هایی که در حالت INFO یا DEBUG لاگ فراوان تولید می‌کنند.
    noisy_loggers = {
        "asyncio": logging.WARNING,
        "httpcore": logging.WARNING,
        "httpx": logging.WARNING,
        "multipart": logging.WARNING,
        "watchfiles": logging.WARNING,
    }

    for logger_name, level in noisy_loggers.items():
        library_logger = logging.getLogger(logger_name)
        library_logger.setLevel(level)

    # Uvicorn گاهی handlerهای خودش را نصب می‌کند. این handlerها پاک می‌شوند
    # تا تمام خروجی‌ها با formatter یکسان به stdout ارسال شوند.
    for logger_name in (
        "uvicorn",
        "uvicorn.error",
    ):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.addHandler(handler)
        uvicorn_logger.propagate = False
        uvicorn_logger.disabled = False

    # چون middleware برنامه هر request را به‌شکل structured ثبت می‌کند،
    # access log داخلی Uvicorn غیرفعال می‌شود تا duplicate log نداشته باشیم.
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers.clear()
    uvicorn_access_logger.propagate = False
    uvicorn_access_logger.disabled = True

    structlog.configure(
        processors=[
            # رخدادهای پایین‌تر از log level در ابتدای pipeline حذف می‌شوند
            # تا metadata، redaction و serialization بی‌دلیل اجرا نشوند.
            structlog.stdlib.filter_by_level,
            *shared_processors,

            # رخداد Structlog را برای پردازش نهایی به ProcessorFormatter
            # متعلق به handler استاندارد logging تحویل می‌دهد.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(
    name: str | None = None,
) -> structlog.stdlib.BoundLogger:
    """
    ساخت logger استاندارد برنامه.

    نام logger معمولاً باید __name__ باشد تا module مبدا در فیلد logger
    خروجی JSON قابل مشاهده و جست‌وجو باشد.
    """

    return structlog.get_logger(name)
