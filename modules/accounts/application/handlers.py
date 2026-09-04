from modules.accounts.application.commands import RegisterAccountCommand
from modules.accounts.application.schemas import (
    AccountResult,
    TokenResult,
    GetCurrentAccountQuery,
)    
from modules.accounts.domain.entities import Account
from modules.accounts.domain.exceptions import (
    AccountAlreadyExistsException,
    InvalidCredentialsException,
    InvalidTokenException,
    AccountNotFoundException
)
from sqlalchemy.exc import IntegrityError

from modules.accounts.domain.repositories import AccountRepository
from shared.security.password import PasswordHasher
from shared.application.uow import UnitOfWork
from modules.accounts.application.commands import (
    LoginCommand, 
    RefreshTokenCommand,
)
from shared.security.jwt import (
    create_access_token, 
    create_refresh_token, 
    decode_token,
)

class RegisterAccountHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        uow: UnitOfWork,
    ) -> None:
        self.repositry = account_repo
        self.password_hasher = password_hasher
        self.uow = uow
    async def handle(self, command: RegisterAccountCommand) -> AccountResult:
        email = str(command.email).lower().strip()

        existing_account = await self.repositry.get_by_email(email)
        if existing_account is not None:
            raise AccountAlreadyExistsException()

        hashed_password = self.password_hasher.hash(command.password)

        account = Account.register(
            email=str(command.email),
            hashed_password=hashed_password,
            first_name=command.first_name,
            last_name=command.last_name,
        )

        try:
            await self.repositry.add(account)
            await self.uow.commit()
        except IntegrityError as exc:
            await self.uow.rollback()
            raise AccountAlreadyExistsException() from exc

        return AccountResult(
            email=account.email,
            first_name=account.first_name,
            last_name=account.last_name,
            is_active=account.is_active,
        )

class LoginHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self.account_repo = account_repo
        self.password_hasher = password_hasher

    async def handle(self, command: LoginCommand) -> TokenResult:
        account = await self.account_repo.get_by_email(command.email)
        if account is None:
            raise InvalidCredentialsException()

        if not account.is_active:
            raise InvalidCredentialsException()

        is_valid = self.password_hasher.verify(
            command.password,
            account.hashed_password,
        )
        if not is_valid:
            raise InvalidCredentialsException()

        access_token = create_access_token(subject=account.id)
        refresh_token = create_refresh_token(subject=account.id)

        return TokenResult(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class RefreshTokenHandler:
    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    async def handle(self, command: RefreshTokenCommand) -> TokenResult:
        payload = decode_token(command.refresh_token)

        if payload.get("type") != "refresh":
            raise InvalidTokenException()

        account_id = payload.get("sub")
        if not account_id:
            raise InvalidTokenException()

        account = await self.account_repo.get_by_id(account_id)
        if account is None or not account.is_active:
            raise InvalidTokenException()

        return TokenResult(
            access_token=create_access_token(subject=account.id),
            refresh_token=create_refresh_token(subject=account.id),
        )


class GetCurrentAccountHandler:
    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    async def handle(self, query: GetCurrentAccountQuery) -> AccountResult:
        account = await self.account_repo.get_by_id(query.account_id)
        if account is None:
            raise AccountNotFoundException()

        return AccountResult(
            email=account.email,
            first_name=account.first_name,
            last_name=account.last_name,
            is_active=account.is_active,
        )