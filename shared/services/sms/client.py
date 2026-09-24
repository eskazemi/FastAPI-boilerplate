from collections.abc import (
    Callable, 
    Mapping,
)
from shared.config import config
from shared.services.sms.interface import SmsClientInterface
from shared.services.sms.iranpayamk import IranPayamakSmsClient
from shared.services.sms.kavenegar import KavenegarClient


class SMS:
    def __init__(self, sms_client: str) -> None:
        self.sms_client = sms_client.lower()

    def get_client(self) -> SmsClientInterface:
        clients: dict[str, Callable[[], SmsClientInterface]] = {
            "kavenegar": lambda: KavenegarClient(
                config.SECRET_KEY_KAVENEGAR.get_secret_value(),
            ),
            "farazsms": lambda: IranPayamakSmsClient(
                config.IRAN_PAYAMK_API_KEY.get_secret_value(),
                config.LINE_NUMBER,
            ),
        }

        try:
            client_factory = clients[self.sms_client]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported SMS client: {self.sms_client}"
            ) from exc

        return client_factory()

    async def send_message(
        self,
        receiver: str,
        message: str | None = None,
        *,
        pattern: bool = False,
        attributes: Mapping[str, str] | None = None,
        pattern_code: str | None = None,
    ) -> str:
        client = self.get_client()

        return await client.send_message(
            receiver=receiver,
            message=message,
            pattern=pattern,
            attributes=attributes,
            pattern_code=pattern_code,
        )
