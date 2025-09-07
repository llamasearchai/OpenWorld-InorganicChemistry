"""Identifier classification and extraction utilities."""

from __future__ import annotations

import re

DOI_REGEX = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
ARXIV_REGEX = re.compile(r"\b(arXiv:)?\d{4}\.\d{4,5}(v\d+)?\b", re.I)
ISBN_REGEX = re.compile(r"\b97[89][- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?[\dX]\b", re.I)
URL_REGEX = re.compile(r"https?://\S+", re.I)


def classify_identifier(value: str) -> str:
    """Classify a single identifier string into a known type.

    Returns one of: "doi", "arxiv", "isbn", "url", or "unknown".
    """
    if DOI_REGEX.search(value):
        return "doi"
    if ARXIV_REGEX.search(value):
        return "arxiv"
    if ISBN_REGEX.search(value):
        return "isbn"
    if URL_REGEX.search(value):
        return "url"
    return "unknown"


def extract_identifiers(text: str) -> list[dict[str, str]]:
    """Extract identifiers from text.

    Returns a list of {"type", "value", "position"} dictionaries.
    """
    results: list[dict[str, str]] = []

    for regex, id_type in [
        (DOI_REGEX, "doi"),
        (ARXIV_REGEX, "arxiv"),
        (ISBN_REGEX, "isbn"),
        (URL_REGEX, "url"),
    ]:
        for match in regex.finditer(text):
            raw_value = match.group(0)
            value = raw_value
            results.append(
                {
                    "type": id_type,
                    "value": value,
                    "position": str(match.start()),
                }
            )

    # Deduplicate by (type, value)
    seen = set()
    unique: list[dict[str, str]] = []
    for item in results:
        key = (item["type"], item["value"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


