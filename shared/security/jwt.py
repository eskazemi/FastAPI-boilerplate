# src/shared/security/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pydantic import BaseModel, Field
from shared.config import config


class TokenPayload(BaseModel):
    sub: str  # شناسه اکانت (account_id)
    exp: datetime
    type: str  # "access" یا "refresh"


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = TokenPayload(
        sub=subject,
        exp=now + expires_delta,
        type=token_type
    )
    return jwt.encode(payload.model_dump(), config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        decoded = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
