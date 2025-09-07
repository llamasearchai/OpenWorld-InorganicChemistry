from __future__ import annotations

import os
import subprocess
import uuid
from datetime import datetime

from ..core.storage import RunRecord, save_run, list_runs


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
    """Generate dynamic report from run DB, support MD and PDF export."""
    if run_id is None:
        run_id = input("Enter run_id to compile: ").strip()  # nosec B322
    # Fetch related runs
    fetched_runs = list_runs(kind="all", limit=10)  # Adjust limit as needed
    results = "\n".join([f"- {r.kind}: {r.output[:100]}..." for r in fetched_runs if r.id == run_id or r.meta.get('related', [])])
    report_text = TEMPLATE.format(
        objective="Automate inorganic PV screening for efficiency and stability.",
        methods="Agents SDK orchestration; ASE/EMT initial energy estimates; literature and synthesis planning via LLM.",
        results=results or f"Compiled outputs associated with run {run_id} (see DB records).",
        next_steps="Integrate production DFT backends and lab data import; add statistical models.",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    out_dir = "reports"
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, f"report_{run_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    # Export to PDF using pandoc
    pdf_path = os.path.join(out_dir, f"report_{run_id}.pdf")
    subprocess.run(["pandoc", md_path, "-o", pdf_path], check=True)
    print("\n=== Report Generated ===\n")
    print(f"MD: {md_path}, PDF: {pdf_path}")
    save_run(RunRecord(id=str(uuid.uuid4()), kind="report", input=run_id, output=f"{md_path}, {pdf_path}", meta={"fetched_count": len(fetched_runs)}))
    return f"{md_path}, {pdf_path}"


