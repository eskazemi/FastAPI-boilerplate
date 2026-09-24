# shared/services/sms/interface.py

from collections.abc import Mapping
from typing import Protocol


class SmsClientInterface(Protocol):
    async def send_message(
        self,
        receiver: str,
        message: str | None = None,
        *,
        pattern: bool = False,
        attributes: Mapping[str, str] | None = None,
        pattern_code: str | None = None,
    ) -> str:
        """Send an SMS and return its message ID."""
        ...
