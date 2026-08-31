from http import HTTPStatus
from shared.exceptions.base import (
    ConflictException, 
    NotFoundException, 
    UnprocessableEntityException,
    CustomException,
    ServiceUnavailableException,
)


class DuplicateValueException(UnprocessableEntityException):
    error_code = "duplicate_value"
    message = "Duplicate value."


class DuplicatePaymentRequestError(ConflictException):
    error_code = "duplicate_payment_request"
    message = "A payment request with the same idempotency key is already in progress."


class PaymentNotFoundError(NotFoundException):
    error_code = "payment_not_found"
    message = "Payment not found."


class AllGatewaysDownError(CustomException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "all_gateways_down"
    message = "All payment gateways are currently unavailable."


class IdempotencyMismatchError(ConflictException):
    """
    همان idempotency key قبلاً با مبلغ یا سفارش دیگری استفاده شده است.
    """
    error_code = "idempotency_mismatch"
    message = (
        "The idempotency key has already been used "
        "with different payment data."
    )


class PaymentGatewayUnavailableError(ServiceUnavailableException):
    """
    هیچ درگاه قابل استفاده‌ای در دسترس نیست.
    """
    error_code = "payment_gateway_unavailable"
    message = "Payment gateway is currently unavailable."


class PaymentRequestFailedError(CustomException):
    """
    درخواست پرداخت به درگاه ارسال شد، اما عملیات ناموفق بود.
    """
    status_code = HTTPStatus.BAD_GATEWAY
    error_code = "payment_request_failed"
    message = "Payment request failed."


# --- خطاهای جدید درخواستی ---

class GatewayTimeoutError(CustomException):
    """
    خطای زمان انتظار (Timeout) در برقراری ارتباط با درگاه پرداخت.
    """
    status_code = HTTPStatus.GATEWAY_TIMEOUT
    error_code = "gateway_timeout"
    message = "Connection to the payment gateway timed out."


class GatewayUnavailableError(ServiceUnavailableException):
    """
    عدم پاسخ‌گویی یا از دسترس خارج بودن موقت درگاه پرداخت هدف.
    """
    error_code = "gateway_unavailable"
    message = "The selected payment gateway is temporarily unavailable."
