# src/modules/account/infrastructure/api/routes.py
from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends,
)
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
)
from modules.accounts.application.schemas import GetCurrentAccountQuery
from shared.infrastructure.api.dependencies import (
    RateLimiter, 
    Limiter, 
    Rate, 
    Duration,
)
from modules.accounts.infrastructure.api.dependencies import (
    get_login_handler,
    get_current_account_handler,
    get_refresh_token_handler,
    get_register_account_handler
)


router = APIRouter(prefix="/accounts", tags=["accounts"])


# Endpointهای Authentication
@router.post("/login", 
            response_model=TokenResponse, 
            dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))])
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
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))]
) -> TokenResponse:
    result = await handler.handle(
        RefreshTokenCommand(refresh_token=payload.refresh_token)
    )

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )

@router.post("", 
            response_model=AccountResponse, 
            status_code=201,
            dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))])
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
        )
    )

    return AccountResponse(
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        is_active=result.is_active,
    )


@router.get("/me", 
            response_model=AccountResponse,
            dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))]
            )
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
        is_active=result.is_active,
    )

