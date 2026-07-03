from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Lead Intake for Bitrix24"
    app_base_url: str = "http://localhost:8000"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite+pysqlite:///./ai_lead_intake.sqlite3"
    database_echo: bool = False
    intake_webhook_secret: str = "dev-webhook-secret"
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: float = 30.0
    confidence_threshold: float = 0.75
    bitrix_mode: str = "mock"
    bitrix_crm_mode: str = "universal"
    bitrix24_webhook_url: str = ""
    bitrix24_base_url: str = ""
    bitrix_timeout_seconds: float = 30.0
    admin_username: str = "admin"
    admin_password: str = "change-me"
    intake_rate_limit_max_requests: int = 30
    intake_rate_limit_window_seconds: int = 60
    legacy_rate_limit_intake: str | None = Field(
        default=None,
        validation_alias="RATE_LIMIT_INTAKE",
    )
    worker_autostart: bool = False
    worker_poll_interval_seconds: float = 2.0
    worker_batch_size: int = 5
    worker_max_retry_attempts: int = 3

    @model_validator(mode="after")
    def apply_legacy_rate_limit(self) -> "Settings":
        if not self.legacy_rate_limit_intake:
            return self

        max_requests, window_seconds = _parse_rate_limit(self.legacy_rate_limit_intake)
        self.intake_rate_limit_max_requests = max_requests
        self.intake_rate_limit_window_seconds = window_seconds
        return self


def _parse_rate_limit(value: str) -> tuple[int, int]:
    normalized = value.strip().lower()
    amount, _, window = normalized.partition("/")
    if not amount or not window:
        raise ValueError(
            "RATE_LIMIT_INTAKE must use the format '<count>/<window>', for example '10/minute'."
        )

    max_requests = int(amount)
    mapping = {
        "second": 1,
        "seconds": 1,
        "minute": 60,
        "minutes": 60,
        "hour": 3600,
        "hours": 3600,
    }
    try:
        window_seconds = mapping[window]
    except KeyError as exc:
        raise ValueError(
            "RATE_LIMIT_INTAKE window must be one of: second, minute, hour."
        ) from exc

    return max_requests, window_seconds


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
