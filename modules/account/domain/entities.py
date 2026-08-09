# src/modules/account/domain/entities.py
from uuid import uuid4

from pydantic import EmailStr, Field

from shared.schemas import AppSchema


class Account(AppSchema):
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    hashed_password: str
    is_active: bool = True

    @classmethod
    def register(cls, email: str, hashed_password: str) -> "Account":
        return cls(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
        )
