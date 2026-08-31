from datetime import (
    datetime, 
    timedelta, 
    timezone,
)
from typing import Any
from uuid import UUID
import jwt
from shared.config import config
from shared.security.exceptions import (
    InvalidTokenException, 
    TokenExpiredException,
)


def create_token(subject: str | UUID, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta

    payload = {
        "sub": str(subject),
        "exp": int(expires_at.timestamp()),
        "type": token_type,
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET.get_secret_value(),
        algorithm=config.JWT_ALGORITHM,
    )


def create_access_token(subject: str | UUID) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(subject: str | UUID) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            config.JWT_SECRET.get_secret_value(),
            algorithms=[config.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredException() from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenException() from exc
