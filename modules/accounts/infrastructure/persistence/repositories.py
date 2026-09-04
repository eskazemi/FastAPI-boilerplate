# src/modules/account/infrastructure/postgres/repositories.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.accounts.domain.entities import Account
from modules.accounts.domain.repositories import AccountRepository
from modules.accounts.infrastructure.persistence.models import AccountModel
from uuid import UUID

class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, account_id: UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is not None else None

    async def get_by_email(self, email: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model is  not None else None

    async def add(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            email=str(account.email),
            first_name=account.first_name,
            last_name=account.last_name,
            hashed_password=account.hashed_password,
            is_active=account.is_active,
        )

        self.session.add(model)

    @staticmethod
    def _to_domain(model: AccountModel) -> Account:
        return Account(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
        )
