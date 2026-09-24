# shared/services/sms/kavenegar.py

import asyncio
import logging
from collections.abc import Mapping

from kavenegar import (
    APIException,
    HTTPException,
    KavenegarAPI,
)

from shared.services.sms.interface import SmsClientInterface


logger = logging.getLogger(__name__)


class KavenegarClient(SmsClientInterface):
    def __init__(self, api_key: str) -> None:
        self.api = KavenegarAPI(api_key)

    def _send_message_sync(
        self,
        receiver: str,
        message: str,
    ) -> str:
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

    async def send_message(
        self,
        receiver: str,
        message: str | None = None,
        *,
        pattern: bool = False,
        attributes: Mapping[str, str] | None = None,
        pattern_code: str | None = None,
    ) -> str:
        if pattern:
            raise NotImplementedError(
                "KavenegarClient does not support pattern SMS"
            )

        if message is None:
            raise ValueError(
                "message is required when pattern=False"
            )

        return await asyncio.to_thread(
            self._send_message_sync,
            receiver,
            message,
        )
