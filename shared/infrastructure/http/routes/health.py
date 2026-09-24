# shared/infrastructure/http/routes/health.py

import asyncio
from collections.abc import Awaitable
from typing import Any
from fastapi import (
    APIRouter, 
    Request, 
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import text

from shared.config import config
from shared.infrastructure.database.postgres import engine
from shared.infrastructure.database.redis import get_redis_db

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live", 
            status_code=status.HTTP_200_OK ,)
async def liveness() -> dict[str, str]:
    """
    فقط زنده بودن process را بررسی می‌کند.

    این endpoint نباید هیچ dependency خارجی مانند
    database، redis یا mirror را بررسی کند.
    """
    return {
        "status": "ok",
        "service": "api",
    }


@router.get("/ready")
async def readiness(request: Request) -> JSONResponse:
    """
    آماده بودن سرویس برای دریافت traffic را بررسی می‌کند.
    """

    database_ok, redis_ok = await asyncio.gather(
        run_check_with_timeout(
            check_database(),
            timeout=3.0,
        ),
        run_check_with_timeout(
            check_redis(),
            timeout=3.0,
        ),
    )

    checks: dict[str, dict[str, Any]] = {
        "database": {
            "status": "ok" if database_ok else "failed",
        },
        "redis": {
            "status": "ok" if redis_ok else "failed",
        },
    }

    is_ready = all(
        check["status"] == "ok"
        for check in checks.values()
    )

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if is_ready
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
        },
    )


async def run_check_with_timeout(
    check: Awaitable[bool],
    timeout: float,
) -> bool:
    try:
        return await asyncio.wait_for(
            check,
            timeout=timeout,
        )
    except Exception:
        return False


async def check_database() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False


async def check_redis() -> bool:
    try:
        redis_manager = get_redis_db()
        redis_client = redis_manager.get_client()

        result = await redis_client.ping()

        return bool(result)

    except Exception:
        return False

