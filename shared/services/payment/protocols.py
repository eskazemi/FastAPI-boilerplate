from typing import Protocol

from .schemas import (
    PaymentRequest,
    PaymentResponse,
    PaymentVerificationResult,
)


class PaymentGateway(Protocol):
    name: str

    async def request_payment(
        self,
        request: PaymentRequest,
    ) -> PaymentResponse:
        ...

    async def verify_payment(
        self,
        authority: str,
        amount: int,
    ) -> PaymentVerificationResult:
        ...
