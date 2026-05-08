# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    webhook_bearer_token: str
    database_url: str

    # AI API keys
    gemini_api_key: str
    groq_api_key: str
    ayrshare_api_key: str = "place_holder_key"
    mock_publishing: bool = False
    cloudinary_url: str = "place_holder_url"

    # Evaluation threshold (0.0 – 1.0)
    eval_score_threshold: float = 0.70

    # Database connection pool settings
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()