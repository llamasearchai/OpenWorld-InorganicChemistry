from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from scipaper.utils.logging_setup import setup_logging
from scipaper.api.v1.routers import system as system_router
from scipaper.api.v1.routers import search as search_router
from scipaper.api.v1.routers import fetch as fetch_router
from scipaper.api.v1.routers import parse as parse_router
from scipaper.agents.server import router as agents_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=60, follow_redirects=True)
    yield
    await app.state.http.aclose()

app = FastAPI(
    title="SciPaper API",
    description="OA-first microservice for paper search/fetch",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

app.include_router(system_router, prefix="/api/v1", tags=["System"])
app.include_router(search_router, prefix="/api/v1", tags=["Search"])
app.include_router(fetch_router, prefix="/api/v1", tags=["Fetch"])
app.include_router(agents_router, prefix="/api/v1", tags=["Agents"])
app.include_router(parse_router, prefix="/api/v1", tags=["Parse"])
