"""Parsing helpers for text and simple formatting of identifier extraction."""

from __future__ import annotations

from .ids import extract_identifiers
import re


def parse_text(text: str, types: list[str] | None = None) -> list[dict[str, str]]:
    """Parse text and extract identifiers, optionally filtering by types."""
    items = extract_identifiers(text)
    # Normalize certain identifier values while preserving raw value in extraction
    for item in items:
        if item.get("type") == "arxiv" and item.get("value"):
            item["value"] = re.sub(r"(?i)^arxiv:", "", item["value"])  # drop prefix for arXiv
    if types:
        wanted = {t.lower() for t in types}
        items = [i for i in items if i.get("type", "").lower() in wanted]
    return items


