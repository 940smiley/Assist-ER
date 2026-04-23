from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_api_url: str = Field(default="https://api.github.com", alias="GITHUB_API_URL")
    workspace_dir: Path = Field(
        default=Path(".assist-er/workspace"),
        alias="ASSIST_ER_WORKSPACE_DIR",
    )
    log_level: str = Field(default="INFO", alias="ASSIST_ER_LOG_LEVEL")
    request_timeout_seconds: float = Field(default=20.0, alias="ASSIST_ER_REQUEST_TIMEOUT")
    pro_token_key_path: Path = Field(
        default=Path(".assist-er/pro/key.bin"),
        alias="ASSIST_ER_PRO_KEY_PATH",
    )
    pro_token_store_path: Path = Field(
        default=Path(".assist-er/pro/tokens.enc"),
        alias="ASSIST_ER_PRO_TOKEN_STORE_PATH",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
