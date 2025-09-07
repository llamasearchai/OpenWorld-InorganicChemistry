"""System health and info endpoints."""

from fastapi import APIRouter

from ....config import is_ollama_available, is_openai_available, settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "openai": is_openai_available(),
        "ollama": is_ollama_available(),
        "version": "1.0.0",
        "downloads_dir": settings.downloads_dir,
    }

@router.options("/health")
async def health_options() -> dict:
    # Explicit OPTIONS handler to satisfy tests without CORS preflight headers
    return {}


