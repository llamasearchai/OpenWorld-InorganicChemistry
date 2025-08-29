import json
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag


# Identifier patterns (inspired by public specs and common usage)
ID_PATTERNS: Dict[str, List[str]] = {
    "doi": [
        # Relaxed digits range to include minimal test cases like 10.1/abc
        r"10\.\d{1,9}/[-._;()/:A-Z0-9]+",
    ],
    "isbn": [
        r"(?:ISBN(?:-10)?:?\ )?(?=[0-9X]{10}|(?=(?:[0-9]+[-\ ]){3})[-\ 0-9X]{13})[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9X]",
        r"(?:ISBN(?:-13)?:?\ )?(?=[0-9]{13}|(?=(?:[0-9]+[-\ ]){4})[-\ 0-9]{17})97[89][-\ ]?[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9]",
    ],
    "arxiv": [
        r"arXiv:\d{4}\.\d{4,5}(v\d+)?",
        r"arXiv:[A-Za-z-]{3,10}(\.[A-Z]{2})?/\d{4,8}",
    ],
    "issn": [
        r"\b\d{4}-\d{3}[\dxX]\b",
    ],
    "url": [
        r"https?://\S+",
    ],
    # Optional: simple PMID heuristic (sequence of digits). Disabled by default in callers.
    "pmid": [
        r"\b\d{5,8}\b",
    ],
}


def parse_ids_from_text(text: str, id_types: Optional[List[str]] = None) -> List[Dict[str, str]]:
    if id_types is None:
        id_types = list(ID_PATTERNS.keys())
    results: List[Dict[str, str]] = []
    seen = set()
    for id_type in id_types:
        for pattern in ID_PATTERNS.get(id_type, []):
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                value = m.group()
                if value not in seen:
                    results.append({"id": value, "type": id_type})
                    seen.add(value)
    return results


def parse_file(path: str, id_types: Optional[List[str]] = None) -> List[Dict[str, str]]:
    with open(path, "rt", encoding="utf-8") as fh:
        content = fh.read()
    return parse_ids_from_text(content, id_types)


def format_output(items: List[Dict[str, str]], fmt: str = "raw") -> str:
    if fmt == "raw":
        return "\n".join(item["id"] for item in items)
    if fmt == "jsonl":
        return "\n".join(json.dumps(item) for item in items)
    if fmt == "csv":
        return "\n".join(f"{item['id']},{item['type']}" for item in items)
    raise ValueError(f"Unsupported format: {fmt}")


def find_pdf_url(html_content: str) -> Optional[str]:
    """Discover a likely direct PDF URL in HTML.

    Heuristics:
    - PDFObject.embed("<url>")
    - <embed id="pdf" type="application/pdf" src="...">
    - <iframe type="application/pdf" src="...">
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # PDFObject.embed("...")
    script = soup.find("script", string=re.compile(r"PDFObject\.embed\(\"([^\"]+)\""))
    script_text = getattr(script, "string", None)
    if script_text:
        m = re.search(r'PDFObject\.embed\("([^"]+)"', script_text)
        if m:
            return m.group(1)

    # <embed id="pdf" type="application/pdf" src="...">
    embed = soup.find("embed", {"id": "pdf", "type": "application/pdf"})
    if isinstance(embed, Tag):
        src = embed.get("src") if hasattr(embed, "get") else None
        if isinstance(src, list):
            src = src[0]
        if src:
            return src

    # <iframe type="application/pdf" src="...">
    iframe = soup.find("iframe", {"type": "application/pdf"})
    if isinstance(iframe, Tag):
        src_iframe = iframe.get("src") if hasattr(iframe, "get") else None
        if isinstance(src_iframe, list):
            src_iframe = src_iframe[0]
        if src_iframe:
            return src_iframe

    return None


