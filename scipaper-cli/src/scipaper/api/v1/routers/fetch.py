from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from pathlib import Path
from scipaper.core.fetcher import Fetcher
from scipaper.utils.ids import classify_identifier

router = APIRouter()


class FetchRequest(BaseModel):

    identifier: str
    output_dir: str = "downloads"
    rename: bool = True


@router.post("/fetch")
async def fetch(req: FetchRequest, request: Request):
    client = request.app.state.http
    fetcher = Fetcher(client)
    kind = classify_identifier(req.identifier)
    meta = {
        "id": req.identifier,
        "title": req.identifier,
        "source": "arxiv" if kind == "arxiv" else "unknown",
        "url": req.identifier if kind == "url" else None
    }
    path = await fetcher.fetch(meta, Path(req.output_dir), rename=req.rename)
    if not path:
        raise HTTPException(404, "Could not fetch via open-access routes.")
    return {"download_path": str(path)}
