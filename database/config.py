from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MongoDB configuration loaded from environment variables."""

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_database: str = Field(
        default="product_assistant",
        alias="MONGODB_DATABASE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()