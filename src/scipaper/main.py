"""Main FastAPI application for SciPaper."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .agents.server import router as agents_router
from .api.v1.routers import fetch, parse, search, system
from .api.v1.routers.advanced_search import router as advanced_search_router
from .api.v1.routers.recommendations import router as recommendations_router
from .config import is_ollama_available, is_openai_available, settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SciPaper API",
        description="A comprehensive scientific paper management and analysis tool",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(system.router, prefix="/api/v1", tags=["System"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(fetch.router, prefix="/api/v1", tags=["Fetch"])
    app.include_router(agents_router, prefix="/api/v1", tags=["Agents"])
    app.include_router(parse.router, prefix="/api/v1", tags=["Parse"])
    app.include_router(advanced_search_router, prefix="/api/v1", tags=["Advanced Search"])
    app.include_router(recommendations_router, prefix="/api/v1", tags=["Recommendations"])

    @app.on_event("startup")
    async def startup_event():
        """Application startup event."""
        logger.info("SciPaper API starting up...")
        try:
            from .sources.registry import list_sources
            logger.info("Available sources: " + ", ".join(list_sources()))
        except Exception:
            logger.warning("Could not determine available sources at startup")

        if is_openai_available():
            logger.info("OpenAI API configured and available")
        else:
            logger.warning("OpenAI API not configured")

        if is_ollama_available():
            logger.info("Ollama configured and available")
        else:
            logger.warning("Ollama not configured")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event."""
        logger.info("SciPaper API shutting down...")

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scipaper.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_debug,
        log_level=settings.log_level.lower(),
    )
    app.include_router(recommendations_router, prefix="/api/v1", tags=["Recommendations"])
