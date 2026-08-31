# shared/infrastructure/http/routes/health.py

from fastapi import (
    APIRouter, 
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import text
from shared.infrastructure.database.postgres import engine

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict:
    return {
        "status": "ok",
        "service": "api",
    }


@router.get("/ready")
async def readiness() -> JSONResponse:
    checks: dict[str, str] = {}

    database_ok = await check_database()
    checks["database"] = "ok" if database_ok else "failed"

    is_ready = all(value == "ok" for value in checks.values())

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
        },
    )


async def check_database() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False
