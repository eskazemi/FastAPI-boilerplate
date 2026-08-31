from pydantic import (
    EmailStr, 
    Field,
)
from uuid import (
    uuid4, 
    UUID,
)

from shared.schemas import AppSchema  
from typing import Annotated

class Account(AppSchema):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    first_name: Annotated[str, Field(min_length=2, max_length=50)]
    last_name: Annotated[str, Field(min_length=2, max_length=50)]
    hashed_password: str
    is_active: bool = True

    @classmethod
    def register(
        cls,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str,
    ) -> "Account":
        return cls(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            is_active=True,
        )
