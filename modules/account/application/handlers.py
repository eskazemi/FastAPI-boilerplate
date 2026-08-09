from modules.account.application.commands import RegisterAccountCommand
from modules.account.application.schemas import AccountResult
from modules.account.domain.entities import Account
from modules.account.domain.exceptions import AccountAlreadyExistsException
from modules.account.domain.repositories import AccountRepository
from shared.security.password import PasswordHasher
from shared.application.uow import UnitOfWork


class RegisterAccountHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        uow: UnitOfWork,
    ) -> None:
        self.account_repo = account_repo
        self.password_hasher = password_hasher
        self.uow = uow

    async def handle(self, command: RegisterAccountCommand) -> AccountResult:
        existing_account = await self.account_repo.get_by_email(str(command.email))

        if existing_account is not None:
            raise AccountAlreadyExistsException()

        hashed_password = self.password_hasher.hash(command.password)

        account = Account.register(
            email=str(command.email),
            hashed_password=hashed_password,
        )

        await self.account_repo.add(account)
        await self.uow.commit()

        return AccountResult(
            id=account.id,
            email=account.email,
            is_active=account.is_active,
        )
