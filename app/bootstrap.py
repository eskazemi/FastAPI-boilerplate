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

from fastapi.responses import JSONResponse

from shared.config import (
    config,
    EnvironmentType,
)
from shared.middlewares.response_logger import (
    ResponseLoggerMiddleware,
)

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
        Middleware(
            CORSMiddleware,
            allow_origins=config.CORS_ALLOW_ORIGINS,
            allow_credentials=config.CORS_ALLOW_CREDENTIALS,
            allow_methods=config.CORS_ALLOW_METHODS,
            allow_headers=config.CORS_ALLOW_HEADERS,
        ),
        Middleware(ResponseLoggerMiddleware),
    ]


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        debug=bool(config.DEBUG),
        docs_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/docs",
        redoc_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/redoc",
        openapi_url=None if config.ENVIRONMENT == EnvironmentType.PRODUCTION else "/openapi.json",
        middleware=make_middleware(),
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

