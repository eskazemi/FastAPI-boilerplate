from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timezone
from typing import Optional


class PaymentStatus(str, Enum):
    INIT = "INIT"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentRequest(BaseModel):
    amount: int = Field(..., gt=0)
    order_id: str = Field(..., min_length=1)
    callback_url: HttpUrl
    customer_id: str | None = None


class PaymentResponse(BaseModel):
    payment_url: HttpUrl
    authority: str
    gateway_name: str
    status: PaymentStatus = PaymentStatus.PENDING


class PaymentVerificationResult(BaseModel):
    authority: str
    gateway_name: str
    reference_id: str | None = None
    status: PaymentStatus
    raw_response: dict | None = None



class IdempotencyRecord(BaseModel):
    order_id: str
    amount: int
    status: str  # "PROCESSING", "COMPLETED", "FAILED"
    response: Optional[PaymentResponse] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )