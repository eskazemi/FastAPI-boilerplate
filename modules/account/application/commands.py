# src/modules/account/application/commands.py
from pydantic import EmailStr, Field

from shared.schemas import AppSchema


class RegisterAccountCommand(AppSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
