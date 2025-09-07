from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover
    keyring = None  # type: ignore

# Load .env if present
load_dotenv(override=False)

KEYCHAIN_SERVICE = "OPENAI_API_KEY"


@dataclass
class Settings:
    openai_api_key: Optional[str]
    model_general: str = os.environ.get("OIC_MODEL_GENERAL", "gpt-4o")
    model_fast: str = os.environ.get("OIC_MODEL_FAST", "gpt-4o-mini")
    verbose: bool = bool(int(os.environ.get("OIC_VERBOSE", "0")))

    @property
    def openai_api_key_masked(self) -> str:
        if not self.openai_api_key:
            return ""
        return self.openai_api_key[:6] + "..." + self.openai_api_key[-4:]

    @staticmethod
    def _from_env() -> Optional[str]:
        key = os.environ.get("OPENAI_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    @staticmethod
    def _from_keychain() -> Optional[str]:
        if keyring is None:
            return None
        try:
            return keyring.get_password(KEYCHAIN_SERVICE, os.environ.get("USER") or "default")
        except Exception:
            return None

    @classmethod
    def load(cls) -> "Settings":
        # Precedence: ENV -> macOS Keychain -> None
        key_env = cls._from_env()
        if key_env:
            return cls(openai_api_key=key_env)
        key_chain = cls._from_keychain()
        return cls(openai_api_key=key_chain)


