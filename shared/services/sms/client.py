from collections.abc import Callable

from services.sms.interface import SmsClientInterface
from services.sms.kavenegar import KavenegarClient
from shared.config import config


class SMS:
    def __init__(
        self,
        sms_client: str,
        receiver: str,
        sms_message: str,
    ) -> None:
        self.sms_client = sms_client
        self.receiver = receiver
        self.sms_message = sms_message

    def get_client(self) -> SmsClientInterface:
        clients: dict[str, Callable[[], SmsClientInterface]] = {
            "kavenegar": lambda: KavenegarClient(
                config.SECRET_KEY_KAVENEGAR.get_secret_value()
            ),
        #     "farazsms": lambda: TwilioClient(
        #         config.FARAZ_API_KEY.get_secret_value()
        #     ),
        }

        try:
            client_factory = clients[self.sms_client]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported SMS client: {self.sms_client}"
            ) from exc

        return client_factory()

    def send_message(self) -> str:
        client = self.get_client()

        return client.send_message(
            self.receiver,
            self.sms_message,
        )
