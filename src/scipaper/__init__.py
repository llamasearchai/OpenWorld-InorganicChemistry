"""SciPaper: A comprehensive scientific paper management and analysis tool."""

__version__ = "1.0.1"
__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai"

from . import agents, api, core, sources, utils
from .config import get_setting, is_ollama_available, is_openai_available, settings
from .exceptions import (
    AgentError,
    AuthenticationError,
    ConfigurationError,
    FetcherError,
    NetworkError,
    ParseError,
    RateLimitError,
    SciPaperError,
    SourceError,
    ValidationError,
)

__all__ = [
    "AgentError",
    "AuthenticationError",
    "ConfigurationError",
    "FetcherError",
    "NetworkError",
    "ParseError",
    "RateLimitError",
    "SciPaperError",
    "SourceError",
    "ValidationError",
    "agents",
    "api",
    "core",
    "get_setting",
    "is_ollama_available",
    "is_openai_available",
    "settings",
    "sources",
    "utils",
]
