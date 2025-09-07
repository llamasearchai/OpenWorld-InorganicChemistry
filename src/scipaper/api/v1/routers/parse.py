"""Parse endpoint for extracting identifiers from text."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ....utils.parse import parse_text


class ParseRequest(BaseModel):
    text: str
    types: Optional[list[str]] = None


router = APIRouter()


@router.post("/parse")
async def parse(req: ParseRequest) -> list[dict[str, str]]:
    return parse_text(req.text, req.types)

