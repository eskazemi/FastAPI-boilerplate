from shared.exceptions.base import UnauthorizedException


class InvalidTokenException(UnauthorizedException):
    message = "Invalid token"


class TokenExpiredException(UnauthorizedException):
    message = "Token has expired"