import httpx
from shared.services.payment.exceptions import (
    GatewayTimeoutError, 
    GatewayUnavailableError,
)
from shared.services.payment.schemas import (
    PaymentRequest, 
    PaymentResponse, 
    PaymentVerificationResult, 
    PaymentStatus,
)


class ZarinPalGateway:
    name = "zarinpal"

    def __init__(
        self,
        merchant_id: str,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._merchant_id = merchant_id
        self._http = http_client

    async def request_payment(
        self,
        request: PaymentRequest,
    ) -> PaymentResponse:
        payload = {
            "merchant_id": self._merchant_id,
            "amount": request.amount,
            "callback_url": str(request.callback_url),
            "description": request.order_id,
        }

        try:
            response = await self._http.post(
                "/payment/request",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GatewayTimeoutError("zarinpal timeout") from exc
        except httpx.HTTPError as exc:
            raise GatewayUnavailableError("zarinpal unavailable") from exc

        data = response.json()

        return PaymentResponse(
            payment_url=f"https://payment.zarinpal.com/pg/StartPay/{data['authority']}",
            authority=data["authority"],
            gateway_name=self.name,
        )

    async def verify_payment(
        self,
        authority: str,
        amount: int,
    ) -> PaymentVerificationResult:
        try:
            response = await self._http.post(
                "/payment/verify",
                json={
                    "merchant_id": self._merchant_id,
                    "authority": authority,
                    "amount": amount,
                },
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GatewayTimeoutError("zarinpal timeout") from exc
        except httpx.HTTPError as exc:
            raise GatewayUnavailableError("zarinpal unavailable") from exc

        data = response.json()

        return PaymentVerificationResult(
            authority=authority,
            gateway_name=self.name,
            reference_id=str(data.get("ref_id")) if data.get("ref_id") else None,
            status=PaymentStatus.SUCCESS,
            raw_response=data,
        )
