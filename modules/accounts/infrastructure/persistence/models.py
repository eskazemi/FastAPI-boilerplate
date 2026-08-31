from sqlalchemy import (
    Boolean, 
    String, 
    UUID
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
)
import uuid
from shared.infrastructure.database.postgres_base import CustomBase


class AccountModel(CustomBase):
    __tablename__ = "accounts"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
