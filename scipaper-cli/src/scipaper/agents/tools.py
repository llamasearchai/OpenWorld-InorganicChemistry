from typing import Dict, Any
from scipaper.sources.arxiv import ArxivSource
from scipaper.core.fetcher import Fetcher
from pathlib import Path

async def tool_search(query: str, context: Dict[str, Any]) -> str:
    """Search arXiv for papers"""
    source = ArxivSource()
    results = await source.search(query, limit=5)
    return "\n".join(
        f"{i+1}. {r['title']} ({r['id']})" 
        for i, r in enumerate(results)
    )

async def tool_fetch(paper_id: str, context: Dict[str, Any]) -> str:
    """Fetch a paper by ID"""
    http = context['http']
    fetcher = Fetcher(http)
    meta = {
        "id": paper_id,
        "title": paper_id,
        "source": "arxiv"
    }
    path = await fetcher.fetch(meta, Path("downloads"))
    return f"Downloaded to: {path}" if path else "Failed to download"


def get_tools() -> Dict[str, Any]:
    """Return all available tools with metadata"""
    return {
        "tool_search": {
            "function": tool_search,
            "description": "Search arXiv for scientific papers",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        },
        "tool_fetch": {
            "function": tool_fetch,
            "description": "Fetch a paper by arXiv ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "arXiv paper ID"}
                },
                "required": ["paper_id"]
            }
        }
    }
