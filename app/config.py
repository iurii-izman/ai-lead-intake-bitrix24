from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Lead Intake for Bitrix24"
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
    worker_autostart: bool = False
    worker_poll_interval_seconds: float = 2.0
    worker_batch_size: int = 5
    worker_max_retry_attempts: int = 3


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
