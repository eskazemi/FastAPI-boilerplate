# src/modules/account/application/schemas.py
from pydantic import EmailStr

from shared.schemas import AppSchema


class AccountResult(AppSchema):
    id: str
    email: EmailStr
    is_active: bool


class TokenResult(AppSchema):
    access_token: str
    refresh_token: str


class GetCurrentAccountQuery(AppSchema):
    account_id: str