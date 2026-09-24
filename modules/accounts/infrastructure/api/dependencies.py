from modules.accounts.infrastructure.persistence.repositories import SqlAlchemyAccountRepository
from shared.infrastructure.database.postgres import get_db_session
from shared.security.password import (
    ArgonPasswordHasher, 
    PasswordHasher,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
from modules.accounts.application.handlers import (
    RegisterAccountHandler,
    LoginHandler,
    RefreshTokenHandler,
    GetCurrentAccountHandler,
)

from shared.infrastructure.database.uow import SqlAlchemyUnitOfWork



def get_password_hasher() -> PasswordHasher:
    return ArgonPasswordHasher()


async def get_register_account_handler(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> RegisterAccountHandler:
    account_repo = SqlAlchemyAccountRepository(session)
    uow = SqlAlchemyUnitOfWork(session)

    return RegisterAccountHandler(
        account_repo=account_repo,
        password_hasher=password_hasher,
        uow=uow,
    )

async def get_current_account_handler(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GetCurrentAccountHandler:
    account_repo = SqlAlchemyAccountRepository(session)
    return GetCurrentAccountHandler(account_repo=account_repo)

async def get_login_handler(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> LoginHandler:
    account_repo = SqlAlchemyAccountRepository(session)
    return LoginHandler(account_repo=account_repo, password_hasher=password_hasher)


async def get_refresh_token_handler(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RefreshTokenHandler:
    account_repo = SqlAlchemyAccountRepository(session)
    return RefreshTokenHandler(account_repo=account_repo)