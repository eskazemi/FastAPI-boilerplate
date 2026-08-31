
#/shared/services/payment/service.py
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from .exceptions import (
    AllGatewaysDownError,
    DuplicatePaymentRequestError,
    IdempotencyMismatchError,
    PaymentGatewayUnavailableError,
    PaymentRequestFailedError,
)
from .factory import GatewayFactory
from .schemas import (
    PaymentRequest, 
    PaymentResponse, 
    IdempotencyRecord,
)


class IdempotencyStore:
    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    def _get_lock_key(self, key: str) -> str:
        return f"payment:idempotency:lock:{key}"

    def _get_result_key(self, key: str) -> str:
        return f"payment:idempotency:result:{key}"

    async def acquire_lock(self, key: str, ttl_seconds: int = 60) -> bool:
        return bool(
            await self._redis.set(
                self._get_lock_key(key),
                "1",
                ex=ttl_seconds,
                nx=True,
            )
        )

    async def release_lock(self, key: str) -> None:
        await self._redis.delete(self._get_lock_key(key))

    async def get_record(self, key: str) -> IdempotencyRecord | None:
        data = await self._redis.get(self._get_result_key(key))
        if not data:
            return None
        return IdempotencyRecord.model_validate_json(data)

    async def save_record(
        self,
        key: str,
        record: IdempotencyRecord,
        ttl_seconds: int = 86400,
    ) -> None:
        await self._redis.set(
            self._get_result_key(key),
            record.model_dump_json(),
            ex=ttl_seconds,
        )


class PaymentService:
    def __init__(
        self,
        redis_client: redis.Redis,
        db_session: AsyncSession,
    ) -> None:
        self.store = IdempotencyStore(redis_client)
        self.db = db_session

    async def create_payment(
        self,
        request: PaymentRequest,
        idempotency_key: str,
    ) -> PaymentResponse:
        existing_record = await self.store.get_record(idempotency_key)
        if existing_record:
            self._validate_fingerprint(existing_record, request)

            if existing_record.status == "COMPLETED" and existing_record.response:
                return existing_record.response

            if existing_record.status == "PROCESSING":
                raise DuplicatePaymentRequestError(
                    "This payment request is already being processed."
                )

        lock_acquired = await self.store.acquire_lock(idempotency_key, ttl_seconds=60)
        if not lock_acquired:
            raise DuplicatePaymentRequestError(
                "Concurrent payment request detected."
            )

        try:
            existing_record = await self.store.get_record(idempotency_key)
            if existing_record:
                self._validate_fingerprint(existing_record, request)

                if existing_record.status == "COMPLETED" and existing_record.response:
                    return existing_record.response

            processing_record = IdempotencyRecord(
                order_id=request.order_id,
                amount=request.amount,
                status="PROCESSING",
                response=None,
            )
            await self.store.save_record(idempotency_key, processing_record, ttl_seconds=300)

            # TODO: create db record in a transaction
            # await self._create_db_payment_record(request, idempotency_key)

            gateway = await GatewayFactory.get_healthy_gateway()
            try:
                response = await gateway.request_payment(request)
            except Exception as exc:
                raise PaymentRequestFailedError(
                    "Payment request to gateway failed."
                ) from exc

            completed_record = IdempotencyRecord(
                order_id=request.order_id,
                amount=request.amount,
                status="COMPLETED",
                response=response,
            )
            await self.store.save_record(idempotency_key, completed_record, ttl_seconds=86400)

            # TODO: update db record with gateway response
            # await self._update_db_payment_record(idempotency_key, response)

            return response

        except AllGatewaysDownError as exc:
            raise PaymentGatewayUnavailableError(
                "No payment gateway is currently available."
            ) from exc

        finally:
            await self.store.release_lock(idempotency_key)

    @staticmethod
    def _validate_fingerprint(record: IdempotencyRecord, request: PaymentRequest) -> None:
        if record.order_id != request.order_id or record.amount != request.amount:
            raise IdempotencyMismatchError(
                "Idempotency key was reused with different order_id or amount."
            )
