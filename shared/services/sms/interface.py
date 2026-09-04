from abc import (
    ABC, 
    abstractmethod,
)


class SmsClientInterface(ABC):
    @abstractmethod
    def send_message(
        self,
        receiver: str,
        message: str,
    ) -> str:
        """Send an SMS message and return its message ID."""
        raise NotImplementedError