# src/shared/infrastructure/exception_handlers.py
from fastapi import (
    FastAPI, 
    Request,
)
from typing import cast
from fastapi.responses import JSONResponse
from datetime import (
    datetime, 
    timezone,
)

from shared.exceptions.base import CustomException


async def custom_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    custom_exc = cast(CustomException, exc)
    return JSONResponse(
        status_code=custom_exc.code.value,
        content={
            "error_code": custom_exc.error_code.value
            if hasattr(custom_exc.error_code, "value")
            else custom_exc.error_code,
            "message": custom_exc.message,
            "detail": custom_exc.message,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error_code": 500,
            "message": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
