"""Search endpoint."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from loguru import logger
from pydantic import BaseModel

from ....api.dependencies import api_key_auth
from ....core.fetcher import Fetcher
from ....exceptions import FetcherError


class SearchRequest(BaseModel):
    query: str
    sources: list[str] | None = None
    limit: int = 10


router = APIRouter()


@router.post("/search", dependencies=[Depends(api_key_auth)])
async def search(req: SearchRequest) -> Page[list[dict[str, Any]]]:
    logger_ctx = logger.bind(
        endpoint="search",
        query=req.query,
        sources=req.sources,
        limit=req.limit,
    )
    try:
        fetcher = Fetcher()
        results = await fetcher.search(req.query, req.sources, req.limit)
        logger_ctx.info("Search endpoint completed successfully")
        return paginate(results)
    except FetcherError as e:
        logger_ctx.error(f"Fetcher error in search: {e}", details=e.details)
        raise HTTPException(status_code=400, detail=f"Search failed: {e.message}") from e
    except Exception as e:
        logger_ctx.error(f"Unexpected error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search") from e
