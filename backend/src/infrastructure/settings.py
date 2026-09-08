from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",
    )


settings = Settings()