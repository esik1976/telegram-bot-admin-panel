from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_secret_key: str = "change-me"
    admin_password: str = "change-me"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bot_admin"
    telegram_bot_token: str = "change-me"
    llm_provider: str = "ollama"
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"
    http_ssl_verify: bool = True
    internal_api_token: str = "change-me"
    backend_api_url: str = "http://127.0.0.1:8000"
    worker_mode: str = "service"
    cors_origins: str = "http://127.0.0.1:3000,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
