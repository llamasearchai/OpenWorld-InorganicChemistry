from __future__ import annotations

import asyncio
import uuid
from typing import Optional

from ..core.storage import RunRecord, save_run
from .prompts import LIT_PROMPT, SYNTH_PROMPT, SIM_PROMPT, ANALYSIS_PROMPT, REPORT_PROMPT


def list_agents() -> list[str]:
    return ["literature", "synthesis", "simulation", "analysis", "reporting"]


def _import_agents_sdk():
    # Try a few likely import paths for the Agents SDK
    try:
        from agents import Agent, Runner  # type: ignore
        return Agent, Runner
    except Exception:
        pass
    try:
        from openai_agents import Agent, Runner  # type: ignore
        return Agent, Runner
    except Exception:
        pass
    try:
        from openai.agents import Agent, Runner  # type: ignore
        return Agent, Runner
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "OpenAI Agents SDK not installed. Install 'openai-agents' or update imports."
        ) from exc


async def run_workflow(input_text: Optional[str] = None, streamed: bool = False) -> str:
    Agent, Runner = _import_agents_sdk()

    literature_agent = Agent(
        name="Literature Agent",
        handoff_description="Finds and summarizes inorganic PV literature with key parameters.",
        instructions=LIT_PROMPT,
    )
    synthesis_agent = Agent(
        name="Synthesis Agent",
        handoff_description="Proposes reproducible synthesis protocols and safety notes.",
        instructions=SYNTH_PROMPT,
    )
    simulation_agent = Agent(
        name="Simulation Agent",
        handoff_description="Plans and explains simulation strategies (ASE/pymatgen/DFT backends).",
        instructions=SIM_PROMPT,
    )
    analysis_agent = Agent(
        name="Analysis Agent",
        handoff_description="Parses outputs, extracts metrics, and proposes follow-up experiments.",
        instructions=ANALYSIS_PROMPT,
    )
    reporting_agent = Agent(
        name="Reporting Agent",
        handoff_description="Compiles results into clean reports (markdown/LaTeX).",
        instructions=REPORT_PROMPT,
    )

    triage_agent = Agent(
        name="Triage Agent",
        instructions="Route the user's solar research task to one of the specialist agents.",
        handoffs=[
            literature_agent,
            synthesis_agent,
            simulation_agent,
            analysis_agent,
            reporting_agent,
        ],
    )

    if input_text is None:
        input_text = input("Enter research task (e.g., 'Summarize perovskite stability'): ").strip()  # nosec B322

    if streamed:
        result = await Runner.run_streamed(triage_agent, input_text)
    else:
        result = await Runner.run(triage_agent, input_text)
    output_text = result.final_output
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="agents",
            input=input_text,
            output=output_text,
            meta={"agent": "triage"},
        )
    )
    print("\n=== AGENT RESULT ===\n")
    print(output_text)
    print(f"\n[run_id] {run_id}")
    return run_id


def run_workflow_sync(input_text: Optional[str] = None, streamed: bool = False) -> str:
    return asyncio.get_event_loop().run_until_complete(run_workflow(input_text, streamed=streamed))


