from typing import Any

from pydantic import BaseModel, ConfigDict


class AppSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class ErrorResponse(AppSchema):
    error_code: int | str
    message: str
    details: dict[str, Any] | None = None
