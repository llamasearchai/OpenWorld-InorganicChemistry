from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import httpx
from scipaper.agents import paper_agents as pa

router = APIRouter()


class AgentRunRequest(BaseModel):


    prompt: str


async def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


@router.post("/agents/run")
async def agents_run(
        body: AgentRunRequest,
        http: httpx.AsyncClient = Depends(get_http)):
    out = await pa.run_agent(body.prompt, http)
    return {"status": "ok", "final": out}
