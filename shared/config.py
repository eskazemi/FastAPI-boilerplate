from enum import Enum
from pydantic import (
    PostgresDsn, 
    RedisDsn, 
    SecretStr,
    Field
)
from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)

from shared.schemas import AppSchema
from typing import Any

class GatewaySettings(AppSchema):
    enabled: bool = True
    fail_max: int = 5
    reset_timeout: int = 300
    options: dict[str, Any] = Field(default_factory=dict)


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: int = 0
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    POSTGRES_URL: PostgresDsn
    REDIS_URL: RedisDsn = "redis://localhost:6379/7"
    
    RELEASE_VERSION: str = "0.1"
    SHOW_SQL_ALCHEMY_QUERIES: int = 0
    
    SECRET_KEY: SecretStr
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CELERY_BROKER_URL: str = "amqp://rabbit:password@localhost:5672"
    CELERY_BACKEND_URL: str = "redis://localhost:6379/0"

    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    APP_NAME: str = "Modular Monolith API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    SECRET_KEY_KAVENEGAR: SecretStr

    PAYMENT_GATEWAY_PRIORITY: list[str] = ["mellat", "zarinpal"]
    PAYMENT_GATEWAYS: dict[str, GatewaySettings] = {
        "mellat": GatewaySettings(
            enabled=True,
            fail_max=5,
            reset_timeout=300,
            options={}  
        ),
        "zarinpal": GatewaySettings(
            enabled=True,
            fail_max=5,
            reset_timeout=300,
            options={}
        )
    }



config: Config = Config()
