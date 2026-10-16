from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "IMKON API"
    environment: str = "development"
    database_url: str
    jwt_secret_key: str = Field(min_length=32)
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    email_code_minutes: int = 15
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    google_client_id: str | None = None
    google_client_secret: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
