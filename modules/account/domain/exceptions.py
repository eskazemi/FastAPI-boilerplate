# src/modules/account/domain/exceptions.py
from shared.exceptions.base import (
    DuplicateValueException, 
    NotFoundException, 
    UnauthorizedException,
)


class AccountNotFoundException(NotFoundException):
    message = "Account not found"


class AccountAlreadyExistsException(DuplicateValueException):
    message = "Account already exists"


class InvalidCredentialsException(UnauthorizedException):
    message = "Invalid credentials"


class InvalidTokenException(UnauthorizedException):
    message = "Invalid Token"

