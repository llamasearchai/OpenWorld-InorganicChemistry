from __future__ import annotations

import textwrap
import uuid
from typing import Optional

from openai import OpenAI

from ..core.settings import Settings
from ..core.storage import RunRecord, save_run
from ..integrations.websearch import web_search


def codex_answer(question: Optional[str] = None, provider: Optional[str] = None, max_results: int = 5) -> str:
    if question is None:
        question = input("Question: ").strip()  # nosec B322
    s = Settings.load()
    if not s.openai_api_key:
        raise RuntimeError("OpenAI API key not configured. See README for setup.")
    client = OpenAI(api_key=s.openai_api_key)

    results = web_search(question, provider=provider, max_results=max_results)
    context = "\n".join([f"- {r.title}\n  {r.url}\n  {r.snippet}" for r in results])
    prompt = textwrap.dedent(
        f"""
        You are a coding and research assistant. Use the following web search results to answer the question.
        Prioritize authoritative sources, synthesize concisely, and include at most 3 inline references as [n].

        Question: {question}

        Web results:
        {context}

        Provide:
        - A direct answer in 3-6 sentences
        - A short checklist of next steps
        - References list mapping [n] to URLs
        """
    ).strip()

    resp = client.responses.create(model=s.model_general, input=prompt)
    output = resp.output_text
    print("\n=== Codex Answer ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(RunRecord(id=run_id, kind="codex", input=question, output=output, meta={"provider": provider or "auto"}))
    print(f"\n[run_id] {run_id}")
    return run_id


