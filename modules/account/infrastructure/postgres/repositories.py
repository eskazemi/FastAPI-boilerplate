# src/modules/account/infrastructure/postgres/repositories.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.account.domain.entities import Account
from modules.account.domain.repositories import AccountRepository
from modules.account.infrastructure.postgres.models import AccountModel


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, account_id: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def get_by_email(self, email: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def add(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            email=str(account.email),
            hashed_password=account.hashed_password,
            is_active=account.is_active,
        )

        self.session.add(model)

    @staticmethod
    def _to_domain(model: AccountModel) -> Account:
        return Account(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
        )
