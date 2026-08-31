from datetime import datetime

from sqlalchemy import (
    Boolean, 
    DateTime, 
    String, 
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from shared.infrastructure.database.postgres_base import CustomBase


class AccountModel(CustomBase):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
