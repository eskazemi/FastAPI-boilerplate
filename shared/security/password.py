# src/shared/infrastructure/security/password_hasher.py
from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordHasher:
    def hash(self, raw_password: str) -> str:
        raise NotImplementedError

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        raise NotImplementedError


class ArgonPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher()

    def hash(self, raw_password: str) -> str:
        return self._hasher.hash(raw_password)

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        try:
            return self._hasher.verify(hashed_password, raw_password)
        except VerifyMismatchError:
            return False
