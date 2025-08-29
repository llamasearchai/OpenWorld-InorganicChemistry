from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from scipaper.sources.arxiv import ArxivSource
from scipaper.sources.crossref import CrossrefSource
from scipaper.sources.semanticscholar import SemanticScholarSource
from scipaper.sources.pubmed import PubMedSource
from scipaper.sources.xrxiv_local import XrxivLocalSource

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    sources: List[str] = ["arxiv"]
    limit: int = 10


@router.post("/search")
async def search(req: SearchRequest) -> Dict[str, Any]:
    srcmap = {
        "arxiv": ArxivSource(),
        "crossref": CrossrefSource(),
        "semanticscholar": SemanticScholarSource(),
        "pubmed": PubMedSource(),
        "xrxiv_local": XrxivLocalSource(),
    }
    papers = []
    for s in req.sources:
        if s in srcmap:
            papers.extend(await srcmap[s].search(req.query, req.limit))
    # dedupe + sort (date desc)
    seen, uniq = set(), []
    for p in papers:
        key = p.get("doi") or (p.get("source"), p.get("id")) or p.get("url")
        if key and key not in seen:
            seen.add(key)
            uniq.append(p)
    uniq = sorted(uniq, key=lambda x: x.get("date", ""), reverse=True)
    return {"papers": uniq}
