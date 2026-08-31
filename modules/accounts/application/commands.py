# src/modules/account/application/commands.py
from pydantic import (
    EmailStr, 
    Field,
)

from shared.schemas import AppSchema

class RegisterAccountCommand(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)


class LoginCommand(AppSchema):
    email: EmailStr
    password: str


class RefreshTokenCommand(AppSchema):
    refresh_token: str