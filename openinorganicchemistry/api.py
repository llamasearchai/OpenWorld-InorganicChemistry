from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agents.literature import literature_query
from .agents.synthesis import propose_synthesis
from .agents.simulation import run_simulation
from .agents.analysis import analyze_results
from .agents.reporting import generate_report
from .agents.orchestration import run_workflow
from .integrations.websearch import web_search
from .agents.codex import codex_answer


app = FastAPI(title="OpenInorganicChemistry API")


class TextRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/agents/run")
async def agents_run(req: TextRequest) -> dict:
    run_id = await run_workflow(req.text)
    return {"run_id": run_id}


@app.post("/literature")
def api_literature(req: TextRequest) -> dict:
    run_id = literature_query(req.text)
    return {"run_id": run_id}


class SynthesisRequest(BaseModel):
    target: str


@app.post("/synthesis")
def api_synthesis(req: SynthesisRequest) -> dict:
    run_id = propose_synthesis(req.target)
    return {"run_id": run_id}


class SimulationRequest(BaseModel):
    formula: str
    backend: str = "emt"
    supercell: int = 1


@app.post("/simulation")
def api_simulation(req: SimulationRequest) -> dict:
    run_id = run_simulation(req.formula, backend=req.backend, supercell=req.supercell)
    return {"run_id": run_id}


class AnalysisRequest(BaseModel):
    path: str


@app.post("/analysis")
def api_analysis(req: AnalysisRequest) -> dict:
    run_id = analyze_results(req.path)
    return {"run_id": run_id}


class ReportRequest(BaseModel):
    run_id: str


@app.post("/report")
def api_report(req: ReportRequest) -> dict:
    path = generate_report(req.run_id)
    return {"path": path}


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("openinorganicchemistry.api:app", host=host, port=port, reload=False)


class SearchRequest(BaseModel):
    query: str
    provider: str = "auto"
    max_results: int = 5


@app.post("/search")
def api_search(req: SearchRequest) -> dict:
    results = web_search(req.query, provider=req.provider, max_results=req.max_results)
    return {
        "results": [
            {"title": r.title, "url": r.url, "snippet": r.snippet}
            for r in results
        ]
    }


class CodexRequest(BaseModel):
    question: str
    provider: str = "auto"
    max_results: int = 5


@app.post("/codex")
def api_codex(req: CodexRequest) -> dict:
    run_id = codex_answer(req.question, provider=req.provider, max_results=req.max_results)
    return {"run_id": run_id}


