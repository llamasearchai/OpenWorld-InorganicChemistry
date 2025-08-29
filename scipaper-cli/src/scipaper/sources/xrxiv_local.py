from typing import Any, Dict, List, Optional
import os
import json


class XrxivLocalSource:
    name = "xrxiv_local"

    def __init__(self, dump_path: Optional[str] = None):
        self.dump_path = dump_path or os.getenv("XRXIV_DUMP_PATH")

    async def search(self, query: str, limit: int, filters: Optional[dict] = None) -> List[Dict[str, Any]]:
        if not self.dump_path or not os.path.exists(self.dump_path):
            return []
        tokens = [t.strip().lower() for t in query.split() if t.strip()]
        out: List[Dict[str, Any]] = []
        with open(self.dump_path, "rt", encoding="utf-8") as fh:
            for line in fh:
                if len(out) >= limit:
                    break
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                text_blob = " ".join([
                    str(rec.get("title", "")),
                    str(rec.get("abstract", "")),
                    " ".join(rec.get("categories", []) if isinstance(rec.get("categories"), list) else []),
                ]).lower()
                if all(tok in text_blob for tok in tokens):
                    authors = rec.get("authors")
                    if isinstance(authors, str):
                        authors_list = [a.strip() for a in authors.split(",") if a.strip()]
                    elif isinstance(authors, list):
                        authors_list = [str(a) for a in authors]
                    else:
                        authors_list = []
                    out.append({
                        "id": rec.get("doi") or rec.get("id") or rec.get("url") or rec.get("title"),
                        "title": rec.get("title"),
                        "authors": authors_list,
                        "date": rec.get("published") or rec.get("date") or rec.get("updated"),
                        "doi": rec.get("doi"),
                        "url": rec.get("pdf_url") or rec.get("url"),
                        "source": self.name,
                    })
        return out


