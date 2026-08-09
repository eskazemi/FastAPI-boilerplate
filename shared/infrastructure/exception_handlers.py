# src/shared/infrastructure/exception_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from shared.exceptions.base import CustomException


async def custom_exception_handler(
    request: Request,
    exc: CustomException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.code.value,
        content={
            "error_code": exc.error_code.value
            if hasattr(exc.error_code, "value")
            else exc.error_code,
            "message": exc.message,
            "detail": exc.detail or exc.message,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CustomException, custom_exception_handler)
