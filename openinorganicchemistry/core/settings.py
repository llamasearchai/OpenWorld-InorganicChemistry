from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
import logging

try:
    import keyring
except ImportError:
    keyring = None  # type: ignore

# Load .env if present
load_dotenv(override=False)

KEYCHAIN_SERVICE = "OPENAI_API_KEY"


@dataclass
class Settings:
    """Settings for the application, loaded from environment or keychain."""
    openai_api_key: Optional[str]
    model_general: str = os.environ.get("OIC_MODEL_GENERAL", "gpt-4o")
    model_fast: str = os.environ.get("OIC_MODEL_FAST", "gpt-4o-mini")
    verbose: bool = bool(int(os.environ.get("OIC_VERBOSE", "0")))

    @property
    def openai_api_key_masked(self) -> str:
        """Masked version of the API key for logging."""
        if not self.openai_api_key:
            return ""
        return self.openai_api_key[:6] + "..." + self.openai_api_key[-4:]

    @staticmethod
    def _from_env() -> Optional[str]:
        """Load API key from environment variable."""
        key = os.environ.get("OPENAI_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    @staticmethod
    def _from_keychain() -> Optional[str]:
        """Load API key from macOS keychain."""
        if keyring is None:
            return None
        try:
            return keyring.get_password(KEYCHAIN_SERVICE, os.environ.get("USER") or "default")
        except Exception:
            return None

    def setup_logging(self) -> None:
        """Set up logging based on verbose flag."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()]
        )

    @classmethod
    def load(cls) -> "Settings":
        """Load and return the settings instance."""
        # Precedence: ENV -> macOS Keychain -> None
        key_env = cls._from_env()
        if key_env:
            settings = cls(openai_api_key=key_env)
        else:
            key_chain = cls._from_keychain()
            settings = cls(openai_api_key=key_chain)
        settings.setup_logging()
        return settings
