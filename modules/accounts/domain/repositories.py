from typing import Protocol

from modules.accounts.domain.entities import Account


class AccountRepository(Protocol):
    async def get_by_id(self, account_id: str) -> Account | None:
        ...

    async def get_by_email(self, email: str) -> Account | None:
        ...

    async def add(self, account: Account) -> None:
        ...
