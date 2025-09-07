from __future__ import annotations

import os
import uuid
from datetime import datetime

from ..core.storage import RunRecord, save_run


TEMPLATE = """# Research Summary

## Objective

{objective}

## Methods

{methods}

## Results

{results}

## Next Steps

{next_steps}

Generated on: {timestamp}
"""


def generate_report(run_id: str | None = None) -> str:
    if run_id is None:
        run_id = input("Enter run_id to compile: ").strip()  # nosec B322
    report_text = TEMPLATE.format(
        objective="Automate inorganic PV screening for efficiency and stability.",
        methods="Agents SDK orchestration; ASE/EMT initial energy estimates; literature and synthesis planning via LLM.",
        results=f"Compiled outputs associated with run {run_id} (see DB records).",
        next_steps="Integrate production DFT backends and lab data import; add statistical models.",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    out_dir = "reports"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"report_{run_id}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print("\n=== Report Generated ===\n")
    print(path)
    save_run(RunRecord(id=str(uuid.uuid4()), kind="report", input=run_id, output=path, meta={}))
    return path


