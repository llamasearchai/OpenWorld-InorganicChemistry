"""Local Xrxiv JSONL source implementation."""

from __future__ import annotations

import json
from typing import Any, Optional

from loguru import logger

from scipaper.config import settings

from ..base_source import BaseSource


class XrxivLocalSource(BaseSource):
    name = "xrxiv"

    def __init__(self, path: Optional[str] = None):
        self.path = path or settings.xrxiv_dump_path

    async def search(self, query: str, limit: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        try:
            results: list[dict[str, Any]] = []
            q = query.lower()
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    if len(results) >= limit:
                        break
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    title = str(item.get("title", ""))
                    abstract = str(item.get("abstract", ""))
                    if q in title.lower() or q in abstract.lower():
                        results.append(
                            {
                                "id": item.get("id") or item.get("doi") or title,
                                "title": title,
                                "authors": item.get("authors", []),
                                "date": item.get("date", ""),
                                "abstract": abstract,
                                "journal": item.get("venue", ""),
                                "doi": item.get("doi", ""),
                                "url": item.get("url", ""),
                                "source": "xrxiv",
                            }
                        )
            return results
        except FileNotFoundError:
            logger.warning(f"Xrxiv dump not found at {self.path}")
            return []
        except Exception as e:
            logger.error(f"Xrxiv search failed: {e}")
            return []

    async def fetch(self, identifier: str, **kwargs: Any) -> Optional[dict[str, Any]]:
        try:
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    if identifier == item.get("id") or identifier == item.get("doi"):
                        title = str(item.get("title", ""))
                        abstract = str(item.get("abstract", ""))
                        return {
                            "id": item.get("id") or item.get("doi") or title,
                            "title": title,
                            "authors": item.get("authors", []),
                            "date": item.get("date", ""),
                            "abstract": abstract,
                            "journal": item.get("venue", ""),
                            "doi": item.get("doi", ""),
                            "url": item.get("url", ""),
                            "source": "xrxiv",
                        }
            return None
        except Exception as e:
            logger.error(f"Xrxiv fetch failed: {e}")
            return None

