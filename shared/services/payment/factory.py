# /payment/factory.py

from __future__ import annotations

import pybreaker
from shared.config import config
from .exceptions import AllGatewaysDownError
from .protocols import PaymentGateway
# from .providers.mellat import MellatGateway
from .providers.Zipal import ZarinPalGateway


class GatewayFactory:
    _gateway_classes: dict[str, type[PaymentGateway]] = {
        # "mellat": MellatGateway,
        "zarinpal": ZarinPalGateway,
    }

    def __init__(self) -> None:
        self._gateways_config = config.PAYMENT_GATEWAYS
        self._priority = config.PAYMENT_GATEWAY_PRIORITY

        # ساخت نمونه‌های Circuit Breaker به صورت پویا بر اساس تنظیمات درگاه‌های فعال
        self._breakers: dict[str, pybreaker.CircuitBreaker] = {
            name: pybreaker.CircuitBreaker(
                fail_max=settings.fail_max,
                reset_timeout=settings.reset_timeout,
                name=name,
            )
            for name, settings in self._gateways_config.items()
            if settings.enabled
        }

    def get_gateway(self, name: str) -> PaymentGateway:
        settings = self._gateways_config.get(name)

        if settings is None:
            raise ValueError(f"Gateway '{name}' is not supported.")

        if not settings.enabled:
            raise ValueError(f"Gateway '{name}' is disabled.")

        gateway_class = self._gateway_classes.get(name)
        if gateway_class is None:
            raise ValueError(f"Gateway '{name}' is not registered in factory metadata.")

        return gateway_class(**settings.options)

    def get_healthy_gateway(self) -> PaymentGateway:
        """
        تلاش برای پیدا کردن و بازگرداندن اولین درگاه در دسترس بر اساس اولویت‌بندی.
        """
        for name in self._priority:
            breaker = self._breakers.get(name)
            if breaker is None:
                continue

            # تا زمانی که وضعیت کلید Open (قطع شده) نباشد، از آن استفاده می‌کنیم
            if breaker.current_state != pybreaker.STATE_OPEN:
                return self.get_gateway(name)

        raise AllGatewaysDownError()

    def get_breaker(self, name: str) -> pybreaker.CircuitBreaker:
        breaker = self._breakers.get(name)
        if breaker is None:
            raise ValueError(f"Breaker for gateway '{name}' is not configured.")
        return breaker


# ساخت یک نمونه سراسری جهت تزریق در بخش‌های مختلف برنامه
gateway_factory = GatewayFactory()
