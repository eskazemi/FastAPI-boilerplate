from typing import Annotated
from pydantic import EmailStr, Field
from shared.schemas import AppSchema

IranMobile = Annotated[
    str,
    Field(
        min_length=11,
        max_length=11,
        pattern=r"^09\d{9}$",
        examples=["09120448744"],
    ),
]


class RegisterAccountRequest(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    mobile: IranMobile


class AccountResponse(AppSchema):
    email: EmailStr
    first_name: str
    last_name: str
    mobile: str
    is_active: bool


class LoginRequest(AppSchema):
    email: EmailStr
    password: str


class TokenResponse(AppSchema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshTokenRequest(AppSchema):
    refresh_token: str


class GetCurrentAccountQuery(AppSchema):
    account_id: str