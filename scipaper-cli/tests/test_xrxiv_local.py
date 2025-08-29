import json
from pathlib import Path
import pytest

from scipaper.sources.xrxiv_local import XrxivLocalSource


@pytest.mark.asyncio
async def test_xrxiv_local_basic(tmp_path: Path):
    dump = tmp_path / "dump.jsonl"
    sample = {
        "title": "Machine learning in biology",
        "abstract": "We apply deep learning to biology.",
        "categories": ["q-bio"],
        "authors": ["Alice", "Bob"],
        "published": "2024-01-02",
        "doi": "10.9/xyz",
        "pdf_url": "https://example.com/p.pdf",
    }
    with open(dump, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps(sample) + "\n")

    src = XrxivLocalSource(str(dump))
    res = await src.search("deep learning biology", 5)
    assert res and res[0]["doi"] == "10.9/xyz" and res[0]["url"].endswith(".pdf")


