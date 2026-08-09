# src/modules/account/infrastructure/api/schemas.py
from pydantic import EmailStr, Field

from shared.schemas import AppSchema


class RegisterAccountRequest(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterAccountResponse(AppSchema):
    id: str
    email: EmailStr
    is_active: bool
