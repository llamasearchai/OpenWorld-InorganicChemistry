from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Optional

from ..core.storage import RunRecord, save_run
from .prompts import LIT_PROMPT, SYNTH_PROMPT, SIM_PROMPT, ANALYSIS_PROMPT, REPORT_PROMPT

logger = logging.getLogger(__name__)

def list_agents() -> list[str]:
    return ["literature", "synthesis", "simulation", "analysis", "reporting"]


def _import_agents_sdk():
    logger.info("Attempting to import Agents SDK")
    # Try a few likely import paths for the Agents SDK
    try:
        from agents import Agent, Runner  # type: ignore
        logger.debug("Imported from agents")
        return Agent, Runner
    except Exception as e:
        logger.warning("Failed to import from agents", exc_info=e)
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
    logger.info("Starting workflow", extra={"streamed": streamed})
    try:
        Agent, Runner = _import_agents_sdk()
    except RuntimeError as e:
        logger.error("Failed to import Agents SDK", exc_info=True)
        raise ValueError(f"Agents SDK is required for workflow. Please install 'openai-agents'. Error: {e}") from e

    # Create agents
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

    shared_state = {"input": input_text}

    # Parallel for independent steps
    lit_task = asyncio.create_task(Runner.run(literature_agent, input_text))
    synth_task = asyncio.create_task(Runner.run(synthesis_agent, input_text))
    lit_result, synth_result = await asyncio.gather(lit_task, synth_task)
    shared_state["literature"] = lit_result.final_output
    shared_state["synthesis"] = synth_result.final_output

    # Chain simulation with previous outputs
    sim_input = f"{input_text}\nLiterature: {shared_state['literature']}\nSynthesis: {shared_state['synthesis']}"
    sim_result = await Runner.run(simulation_agent, sim_input)
    shared_state["simulation"] = sim_result.final_output

    # Chain analysis
    analysis_input = f"Analyze based on previous: {shared_state['simulation']}"
    analysis_result = await Runner.run(analysis_agent, analysis_input)
    shared_state["analysis"] = analysis_result.final_output

    # Reporting with all state
    report_input = "\n".join([f"{k}: {v}" for k, v in shared_state.items()])
    report_result = await Runner.run(reporting_agent, report_input)
    output_text = report_result.final_output

    if input_text is None:
        input_text = input("Enter research task (e.g., 'Summarize perovskite stability'): ").strip()  # nosec B322
    if not input_text:
        raise ValueError("Research task input cannot be empty. Please provide a valid query.")

    # Output already produced via reporting_agent
    run_id = str(uuid.uuid4())
    logger.info("Workflow completed", extra={"run_id": run_id, "output_length": len(output_text)})
    save_run(
        RunRecord(
            id=run_id,
            kind="agents",
            input=input_text,
            output=output_text,
            meta={"agents_run": list(shared_state.keys())},
        )
    )
    print("\n=== AGENT RESULT ===\n")
    print(output_text)
    print(f"\n[run_id] {run_id}")
    return run_id


def run_workflow_sync(input_text: Optional[str] = None, streamed: bool = False) -> str:
    return asyncio.get_event_loop().run_until_complete(run_workflow(input_text, streamed=streamed))


