from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    dsn: str = "postgresql://postgres:postgres@localhost:5432/food_receipt"
    min_pool_size: int = 1
    max_pool_size: int = 5


class LLMSettings(BaseModel):
    google_api_key: str
    model_name: str = "gemini-3.5-flash"


class StorageSettings(BaseModel):
    receipts_dir: Path = Path("data/receipts")


class Settings(BaseSettings):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings
    storage: StorageSettings = Field(default_factory=StorageSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
