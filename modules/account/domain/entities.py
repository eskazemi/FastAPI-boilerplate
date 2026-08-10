from uuid import uuid4
from pydantic import EmailStr, Field
from shared.schemas import AppSchema  
from typing import Annotated
from shared.types import PersianMobile

class Account(AppSchema):
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    mobile_number: PersianMobile
    first_name: Annotated[str, Field(min_length=2, max_length=50)]
    last_name: Annotated[str, Field(min_length=2, max_length=50)]
    hashed_password: str
    is_active: bool = True

    @classmethod
    def register(
        cls,
        email: str,
        mobile_number: str,
        first_name: str,
        last_name: str,
        hashed_password: str,
    ) -> "Account":
        return cls(
            email=email,
            mobile_number=mobile_number,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            is_active=True,
        )
