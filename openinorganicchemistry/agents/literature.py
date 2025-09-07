from __future__ import annotations

import uuid

from openai import OpenAI  # Responses API
from ..core.settings import Settings
from ..core.storage import RunRecord, save_run
from ..integrations.lit_sources import search_arxiv, search_crossref


def literature_query(topic: str | None = None) -> str:
    if topic is None:
        topic = input("Enter research topic (e.g., 'perovskite stability'): ").strip()  # nosec B322
    s = Settings.load()
    if not s.openai_api_key:
        raise RuntimeError("OpenAI API key not configured. See README for setup.")
    client = OpenAI(api_key=s.openai_api_key)
    papers = search_arxiv(topic, max_results=5) + search_crossref(topic, max_results=5)
    bullet = "\n".join([f"- {p.title} ({p.year}) — {p.url}" for p in papers])
    prompt = (
        f"You are a PV literature assistant. Given this topic: {topic}\n\n"
        f"Here is a short list of potentially relevant recent papers (from arXiv and Crossref):\n{bullet}\n\n"
        "Please produce a concise bullet summary with key parameters (band gap, stability, synthesis, device architecture) where available, and suggest 3 next steps."
    )
    resp = client.responses.create(model=s.model_general, input=prompt)
    output = resp.output_text
    print("\n=== Literature Summary ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="literature",
            input=topic,
            output=output,
            meta={"model": s.model_general},
        )
    )
    print(f"\n[run_id] {run_id}")
    return run_id


