"""Application configuration for sync worker."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings."""

    notion_token: str
    notion_database_id: str
    gcal_calendar_id: str = "primary"
    timezone: str = "Asia/Seoul"
    contact_file: str = "contact.json"
    token_file: str = "token.json"
    credentials_file: str = "credentials.json"
    dry_run: bool = False
    page_size: int = 100
    max_retries: int = 3
    retry_base_seconds: float = 0.3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
