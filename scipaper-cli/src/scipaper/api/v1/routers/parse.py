from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from scipaper.utils.parse import parse_file, parse_ids_from_text, format_output, ID_PATTERNS


router = APIRouter()


class ParseRequest(BaseModel):
    text: Optional[str] = None
    path: Optional[str] = None
    types: Optional[List[str]] = None
    format: str = "raw"


@router.post("/parse")
async def parse_ids(body: ParseRequest) -> Dict[str, Any]:
    if (body.text is None) == (body.path is None):
        raise HTTPException(400, "Provide exactly one of 'text' or 'path'.")
    if body.types is not None:
        for t in body.types:
            if t not in ID_PATTERNS:
                raise HTTPException(400, f"Unsupported id type: {t}")

    items = parse_file(body.path, body.types) if body.path else parse_ids_from_text(body.text or "", body.types)
    formatted = format_output(items, body.format)
    return {"matches": items, "formatted": formatted}


