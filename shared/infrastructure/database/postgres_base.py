#shared/infrastructure/database/postgres_base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column, 
    DateTime, 
    func,
)

class Base(DeclarativeBase):
    pass

class CustomBase(Base):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)