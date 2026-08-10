from typing import Annotated

from pydantic import Field

PersianMobile = Annotated[
    str,
    Field(
        min_length=11,
        max_length=11,
        pattern=r"^09\d{9}$",
        examples=["09120448744"],
    ),
]
