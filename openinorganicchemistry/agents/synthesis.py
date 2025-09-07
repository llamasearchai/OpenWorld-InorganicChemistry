from __future__ import annotations

import uuid
from openai import OpenAI

from ..core.settings import Settings
from ..core.storage import RunRecord, save_run


def propose_synthesis(target: str | None = None) -> str:
    if target is None:
        target = input("Target material (e.g., CH3NH3PbI3): ").strip()  # nosec B322
    s = Settings.load()
    if not s.openai_api_key:
        raise RuntimeError("OpenAI API key not configured. See README for setup.")
    client = OpenAI(api_key=s.openai_api_key)
    prompt = (
        f"Propose a reproducible inorganic synthesis route for {target}. "
        "Include solvents, precursors, temperatures, atmospheres, annealing, "
        "and safety notes with alternatives when hazardous."
    )
    resp = client.responses.create(model=s.model_general, input=prompt)
    output = resp.output_text
    print("\n=== Suggested Synthesis Pathway ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="synthesis",
            input=target,
            output=output,
            meta={"model": s.model_general},
        )
    )
    print(f"\n[run_id] {run_id}")
    return run_id


