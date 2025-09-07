"""Agents API router."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from .paper_agents import generate_response


class AgentRequest(BaseModel):
    prompt: str


router = APIRouter()


@router.post("/agents/run")
async def run_agent(req: AgentRequest) -> dict[str, Any]:
    content = await generate_response(req.prompt)
    return {"content": content}


