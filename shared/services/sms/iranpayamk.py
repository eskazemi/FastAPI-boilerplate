# shared/services/sms/iranpayamak.py

import asyncio
import json
import logging
from collections.abc import Mapping
import requests
from shared.services.sms.interface import SmsClientInterface


logger = logging.getLogger(__name__)


class IranPayamakSmsClient(SmsClientInterface):
    def __init__(
        self,
        api_key: str,
        line_number: str,
        timeout: tuple[float, float] = (5.0, 15.0),
    ) -> None:
        self.url = (
            "https://api.iranpayamak.com/ws/v1/sms/pattern"
        )
        self.headers = {
            "Accept": "application/json",
            "Api-Key": api_key,
        }
        self.line_number = line_number
        self.timeout = timeout

    def _send_pattern_message_sync(
        self,
        receiver: str,
        attributes: Mapping[str, str],
        pattern_code: str,
    ) -> str:
        payload = {
            "code": pattern_code,
            "attributes": {
                key: str(value)
                for key, value in attributes.items()
            },
            "recipient": receiver,
            "line_number": self.line_number,
            "number_format": "english",
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.RequestException:
            logger.exception(
                "IranPayamak API error while sending pattern SMS"
            )
            raise

        try:
            data = response.json()
        except ValueError:
            return response.text

        if isinstance(data, dict):
            for key in ("messageid", "message_id", "id"):
                if data.get(key) is not None:
                    return str(data[key])

        return json.dumps(data, ensure_ascii=False)

    async def send_message(
        self,
        receiver: str,
        message: str | None = None,
        *,
        pattern: bool = False,
        attributes: Mapping[str, str] | None = None,
        pattern_code: str | None = None,
    ) -> str:
        if not pattern:
            raise NotImplementedError(
                "IranPayamakSmsClient currently supports pattern SMS only"
            )

        if attributes is None:
            raise ValueError(
                "attributes is required when pattern=True"
            )

        if pattern_code is None:
            raise ValueError(
                "pattern_code is required when pattern=True"
            )

        if message is not None:
            logger.warning(
                "message is ignored for IranPayamak pattern SMS"
            )

        return await asyncio.to_thread(
            self._send_pattern_message_sync,
            receiver,
            attributes,
            pattern_code,
        )
