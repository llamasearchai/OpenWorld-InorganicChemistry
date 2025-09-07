from .agents.server import router as agents_router
from .api.v1.routers import fetch, parse, search, system
from .api.v1.routers.advanced_search import router as advanced_search_router
from .api.v1.routers.recommendations import router as recommendations_router
from .config import is_ollama_available, is_openai_available, settings
