# src/shared/security/dependencies.py

from typing import Annotated
from uuid import UUID
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from shared.exceptions.base import UnauthorizedException
from shared.security.context import AuthenticatedUser
from shared.security.jwt import decode_token


class InvalidTokenException(UnauthorizedException):
    message = "Invalid Token"


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    if credentials is None:
        raise InvalidTokenException()

    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise InvalidTokenException()

    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenException()

    try:
        account_id = UUID(str(subject))
    except ValueError as exc:
        raise InvalidTokenException() from exc

    return AuthenticatedUser(id=account_id)
