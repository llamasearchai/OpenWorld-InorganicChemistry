from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FASTAPI_HOST: str = "127.0.0.1"
    FASTAPI_PORT: int = 8000
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_HOST: Optional[str] = "host.docker.internal"
    ALLOW_UNAUTHORIZED_SOURCES: bool = False

    # Load environment variables from .env at project root; allow extra keys
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
