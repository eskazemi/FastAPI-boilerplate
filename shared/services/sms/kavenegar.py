import logging

from kavenegar import (
    APIException,
    HTTPException,
    KavenegarAPI,
)
from services.sms.interface import SmsClientInterface


logger = logging.getLogger(__name__)


class KavenegarClient(SmsClientInterface):
    def __init__(self, api_key: str) -> None:
        self.api = KavenegarAPI(api_key)

    def send_message(
        self,
        receiver: str,
        message: str,
    ) -> str:
        """Send an SMS message using the Kavenegar API."""

        params = {
            "receptor": receiver,
            "message": message,
        }

        try:
            response = self.api.sms_send(params)
            return str(response.messageid)

        except APIException:
            logger.exception(
                "Kavenegar API error while sending SMS"
            )
            raise

        except HTTPException:
            logger.exception(
                "Kavenegar HTTP error while sending SMS"
            )
            raise
