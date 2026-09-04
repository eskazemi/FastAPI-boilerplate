from fastapi import Request

from shared.logging import get_logger


def get_request_logger(request: Request):
    """
    Logger دارای context مربوط به Request جاری.

    request_id و سایر فیلدها توسط Middleware با contextvars
    به‌صورت خودکار اضافه می‌شوند.
    """

    return get_logger(request.scope.get("endpoint", "api"))