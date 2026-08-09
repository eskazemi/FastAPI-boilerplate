# src/modules/account/infrastructure/api/routes.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from modules.account.application.commands import RegisterAccountCommand
from modules.account.application.handlers import RegisterAccountHandler
from modules.account.infrastructure.api.schemas import (
    RegisterAccountRequest,
    RegisterAccountResponse,
)
from modules.account.infrastructure.postgres.repositories import SqlAlchemyAccountRepository
from shared.infrastructure.postgres import get_db_session
from shared.security.password import ArgonPasswordHasher, PasswordHasher
from shared.infrastructure.uow import SqlAlchemyUnitOfWork

router = APIRouter(prefix="/accounts", tags=["accounts"])


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


@router.post("", response_model=RegisterAccountResponse, status_code=201)
async def register_account(
    payload: RegisterAccountRequest,
    handler: Annotated[RegisterAccountHandler, Depends(get_register_account_handler)],
) -> RegisterAccountResponse:
    result = await handler.handle(
        RegisterAccountCommand(
            email=payload.email,
            password=payload.password,
        )
    )

    return RegisterAccountResponse(
        id=result.id,
        email=result.email,
        is_active=result.is_active,
    )
