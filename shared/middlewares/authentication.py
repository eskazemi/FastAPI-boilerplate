# shared/infrastructure/http/middlewares/authentication.py

from dataclasses import dataclass
from typing import Any

from jose import JWTError, jwt
from starlette.authentication import (
    AuthCredentials, 
    AuthenticationBackend, 
    BaseUser,
)
from starlette.middleware.authentication import (
    AuthenticationMiddleware as StarletteAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from shared.config import config


@dataclass(frozen=True)
class CurrentUser(BaseUser):
    id: str
    claims: dict[str, Any]

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.id


class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, CurrentUser] | None:
        authorization = conn.headers.get("Authorization")
        if not authorization:
            return None

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None

        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
        except JWTError:
            return None

        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            return None

        current_user = CurrentUser(
            id=str(user_id),
            claims=payload,
        )

        return AuthCredentials(["authenticated"]), current_user


class AuthenticationMiddleware(StarletteAuthenticationMiddleware):
    pass
