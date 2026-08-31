# src/modules/account/application/schemas.py
from pydantic import EmailStr
from uuid import UUID
from shared.schemas import AppSchema


class AccountResult(AppSchema):
    email: EmailStr
    is_active: bool
    first_name: str
    last_name: str


class TokenResult(AppSchema):
    access_token: str
    refresh_token: str


class GetCurrentAccountQuery(AppSchema):
    account_id: UUID