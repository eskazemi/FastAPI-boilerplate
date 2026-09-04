from pydantic import (
    EmailStr, 
    Field,
)
from uuid import UUID
from shared.schemas import AppSchema

class RegisterAccountRequest(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)


class AccountResponse(AppSchema):
    email: EmailStr
    first_name: str
    last_name: str
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
