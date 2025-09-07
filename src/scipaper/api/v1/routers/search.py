"""Search endpoint."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from loguru import logger

from ....core.fetcher import Fetcher
from ....api.dependencies import api_key_auth
from ....exceptions import FetcherError
from fastapi_pagination import Page, paginate


class SearchRequest(BaseModel):
    query: str
    sources: Optional[list[str]] = None
    limit: int = 10


router = APIRouter()


@router.post("/search", dependencies=[Depends(api_key_auth)])
async def search(req: SearchRequest, api_key: str) -> Page[list[dict[str, Any]]]:
    logger_ctx = logger.bind(endpoint="search", query=req.query, sources=req.sources, limit=req.limit)
    try:
        fetcher = Fetcher()
        results = await fetcher.search(req.query, req.sources, req.limit)
        logger_ctx.info("Search endpoint completed successfully")
        return paginate(results)
    except FetcherError as e:
        logger_ctx.error(f"Fetcher error in search: {e}", details=e.details)
        raise HTTPException(status_code=400, detail=f"Search failed: {e.message}")
    except Exception as e:
        logger_ctx.error(f"Unexpected error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search")

