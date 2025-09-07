"""Fetch endpoint."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from loguru import logger

from ....api.dependencies import api_key_auth
from ....core.fetcher import Fetcher
from ....exceptions import FetcherError


class FetchRequest(BaseModel):
    identifier: str
    source: Optional[str] = None


router = APIRouter()


@router.post("/fetch", dependencies=[Depends(api_key_auth)])
async def fetch(req: FetchRequest, api_key: str) -> Optional[dict[str, Any]]:
    logger_ctx = logger.bind(endpoint="fetch", identifier=req.identifier, source=req.source)
    try:
        fetcher = Fetcher()
        result = await fetcher.fetch(req.identifier, req.source)
        logger_ctx.info("Fetch endpoint completed successfully")
        return result
    except FetcherError as e:
        logger_ctx.error(f"Fetcher error in fetch: {e}", details=e.details)
        raise HTTPException(status_code=400, detail=f"Fetch failed: {e.message}")
    except Exception as e:
        logger_ctx.error(f"Unexpected error in fetch endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during fetch")

