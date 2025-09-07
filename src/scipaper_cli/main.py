import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scipaper_cli.utils.logging_setup import setup_logging
from scipaper_cli.api.v1.routers import system as system_router
from scipaper_cli.api.v1.routers import search as search_router
from scipaper_cli.api.v1.routers import fetch as fetch_router
from scipaper_cli.api.v1.routers import parse as parse_router
from scipaper_cli.agents.server import router as agents_router

# Setup logging
setup_logging()
