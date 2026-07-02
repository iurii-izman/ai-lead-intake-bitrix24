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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
