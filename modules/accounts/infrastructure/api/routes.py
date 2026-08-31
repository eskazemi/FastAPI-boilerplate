# src/modules/account/infrastructure/api/routes.py
from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession
from modules.accounts.application.commands import (
    LoginCommand, 
    RefreshTokenCommand,
)
from shared.security.context import AuthenticatedUser
from shared.security.dependencies import get_current_user
from modules.accounts.application.commands import RegisterAccountCommand
from modules.accounts.application.handlers import (
    RegisterAccountHandler,
    LoginHandler,
    RefreshTokenHandler,
    GetCurrentAccountHandler,
)
from modules.accounts.infrastructure.api.schemas import (
    RegisterAccountRequest,
    AccountResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    GetCurrentAccountQuery,
)
from modules.accounts.infrastructure.persistence.repositories import SqlAlchemyAccountRepository
from shared.infrastructure.database.postgres import get_db_session
from shared.security.password import (
    ArgonPasswordHasher, 
    PasswordHasher,
)
from shared.infrastructure.database.uow import SqlAlchemyUnitOfWork

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


# Endpointهای Authentication
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    handler: Annotated[LoginHandler, Depends(get_login_handler)],
) -> TokenResponse:
    result = await handler.handle(
        LoginCommand(
            email=payload.email,
            password=payload.password,
        )
    )

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    handler: Annotated[RefreshTokenHandler, Depends(get_refresh_token_handler)],
) -> TokenResponse:
    result = await handler.handle(
        RefreshTokenCommand(refresh_token=payload.refresh_token)
    )

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

@router.post("", response_model=AccountResponse, status_code=201)
async def register_account(
    payload: RegisterAccountRequest,
    handler: Annotated[RegisterAccountHandler, Depends(get_register_account_handler)],
) -> AccountResponse:
    result = await handler.handle(
        RegisterAccountCommand(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            mobile=payload.mobile,
        )
    )

    return AccountResponse(
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        mobile=result.mobile,
        is_active=result.is_active,
    )


@router.get("/me", response_model=AccountResponse)
async def get_my_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    handler: Annotated[GetCurrentAccountHandler, Depends(get_current_account_handler)],
) -> AccountResponse:
    result = await handler.handle(
        GetCurrentAccountQuery(account_id=current_user.id)
    )

    return AccountResponse(
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        mobile=result.mobile,
        is_active=result.is_active,
    )