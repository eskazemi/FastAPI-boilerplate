from collections.abc import Sequence
from fastapi import (
    FastAPI, 
    Request,
)
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from shared.infrastructure.exception_handlers import register_exception_handlers
from shared.infrastructure.http.routes.health import router as health_router
from modules.accounts.infrastructure.api.routes import router as account_router
from shared.cache.cache_manager import Cache
from shared.cache.custom_key_maker import CustomKeyMaker
from shared.cache.redis_backend import RedisBackend
from shared.logging import (
    configure_logging, 
    get_logger,
)
from shared.middlewares.request_logging import RequestLoggingMiddleware
from fastapi.responses import JSONResponse
from shared.config import (
    config,
    EnvironmentType,
)
from contextlib import asynccontextmanager


configure_logging()
logger = get_logger(__name__)


def register_cache() -> None:
    Cache.init(
        backend=RedisBackend(),
        key_maker=CustomKeyMaker(),
    )

def on_auth_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "message": "Authentication failed",
        },
    )


def make_middleware() -> Sequence[Middleware]:
    return [
        Middleware(RequestLoggingMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=config.CORS_ALLOW_ORIGINS,
            allow_credentials=config.CORS_ALLOW_CREDENTIALS,
            allow_methods=config.CORS_ALLOW_METHODS,
            allow_headers=config.CORS_ALLOW_HEADERS,
        ),

    ]


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    Lifecycle مدیریت چرخه عمر اپلیکیشن با پشتیبانی کامل از FastAPI.

    این context manager یکپارچه با ASGI server (uvicorn/gunicorn) کار می‌کند.
    بخش startup قبل از `yield` اجرا می‌شود و بخش shutdown در هنگام بستن اپلیکیشن (KeyboardInterrupt، graceful shutdown، یا restart) فراخوانی می‌شود.
    """

    # لاگ شروع اپلیکیشن (قبل از ثبت cache و منابع دیگر)
    logger.info(
        "application_starting",
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
    )

    # Startup: ثبت منابع و اتصالات اولیه
    register_cache()

    # TODO: اینجا منابع دیگر را مقداردهی کنید
    # - database (SQLAlchemy session, asyncpg, etc.)
    # - redis (اگر Cache.init کافی نبود، اتصال مستقیم)
    # - rabbitmq (pika یا aio_pika connection)
    # - mongo (pymongo AsyncClient یا motor)
    # - clients خارجی (HTTP, gRPC, WebSocket, etc.)

    try:
        yield
    finally:
        # Shutdown: بستن امن منابع (همگام و ایمن)
        # - بستن connection poolهای دیتابیس
        # - بستن اتصال redis
        # - بستن message broker (rabbitmq)
        # - بستن mongo clients
        # - بستن هر client دیگر

        logger.info("application_stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        debug=bool(config.DEBUG),
        docs_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/docs",
        redoc_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/redoc",
        openapi_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/openapi.json",
        middleware=make_middleware(),
        lifespan=lifespan,
    )
    register_routers(app)
    register_cache()
    register_exception_handlers(app)


    return app

def register_routers(app: FastAPI):
    app.include_router(health_router)
    app.include_router(account_router)

    # بعدا routerهای ماژول‌ها اینجا اضافه می‌شوند:
    #
    # from modules.account.presentation.http.router import router as account_router
    # app.include_router(account_router, prefix="/accounts", tags=["accounts"])
    #
    # from modules.profile.presentation.http.router import router as profile_router
    # app.include_router(profile_router, prefix="/profiles", tags=["profiles"])

    #     # فعال‌سازی سرویس‌ها بر اساس فِلگ
    # if os.getenv("ENABLE_USER_SERVICE", "true").lower() == "true":
    #     app.include_router(user_router, prefix="/users")
    #     print("✅ سرویس کاربران فعال شد")
    
    # if os.getenv("ENABLE_ORDERS_SERVICE", "true").lower() == "true":
    #     app.include_router(orders_router, prefix="/orders")
    #     print("✅ سرویس سفارشات فعال شد")
    
    # if os.getenv("ENABLE_ANALYTICS_SERVICE", "true").lower() == "true":
    #     app.include_router(analytics_router, prefix="/analytics")
    #     print("✅ سرویس تحلیلات فعال شد")
    return app

