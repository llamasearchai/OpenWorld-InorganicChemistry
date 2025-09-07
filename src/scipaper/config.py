"""Centralized configuration management for SciPaper."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    fastapi_host: str = Field(default="0.0.0.0", env="FASTAPI_HOST")
    fastapi_port: int = Field(default=8000, env="FASTAPI_PORT")
    fastapi_debug: bool = Field(default=False, env="FASTAPI_DEBUG")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.2, env="OPENAI_TEMPERATURE")

    # Ollama Configuration
    ollama_host: str = Field(default="localhost", env="OLLAMA_HOST")
    ollama_port: int = Field(default=11434, env="OLLAMA_PORT")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")

    # External API Configuration
    crossref_user_agent: str = Field(
        default="SciPaper/1.0 (mailto:nikjois@llamasearch.ai)",
        env="CROSSREF_USER_AGENT"
    )
    semanticscholar_api_key: Optional[str] = Field(
        default=None, env="SEMANTICSCHOLAR_API_KEY"
    )
    pubmed_email: str = Field(
        default="scipaper@example.com", env="PUBMED_EMAIL"
    )
    pubmed_api_key: Optional[str] = Field(
        default=None, env="PUBMED_API_KEY"
    )

    # File Paths
    downloads_dir: str = Field(default="./downloads", env="DOWNLOADS_DIR")
    xrxiv_dump_path: str = Field(default="./data/xrxiv.jsonl", env="XRXIV_DUMP_PATH")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_setting(key: str, default=None):
    """Get a setting value by key."""
    return getattr(settings, key, default)


def is_openai_available() -> bool:
    """Check if OpenAI API is configured."""
    return bool(settings.openai_api_key)


def is_ollama_available() -> bool:
    """Check if Ollama is configured."""
    return bool(settings.ollama_host and settings.ollama_port)
