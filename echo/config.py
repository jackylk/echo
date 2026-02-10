"""Configuration management for Echo"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Echo configuration settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Claude API
    anthropic_api_key: str

    # NeuroMemory API
    neuromemory_api_key: str
    neuromemory_base_url: str = "http://localhost:8765"

    # Echo settings
    echo_user_id: str = "default_user"
    echo_log_level: str = "INFO"

    # Optional: OpenAI
    openai_api_key: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
