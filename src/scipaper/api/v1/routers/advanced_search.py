"""Advanced search API endpoint."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ....core.advanced_search import advanced_search, parse_search_query


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search."""

    query: str = Field(..., description="Search query")
    sources: Optional[List[str]] = Field(None, description="Sources to search")
    limit: int = Field(20, ge=1, le=100, description="Maximum results to return")
    semantic_search: bool = Field(False, description="Enable semantic search expansion")
    ranking_method: str = Field(
        "relevance",
        description="Ranking method",
        pattern="^(relevance|date|citations)$",
    )

    # Advanced filters
    date_range_start: Optional[int] = Field(None, ge=1900, le=2030,
                                          description="Start year for date range")
    date_range_end: Optional[int] = Field(None, ge=1900, le=2030,
                                        description="End year for date range")
    authors: Optional[List[str]] = Field(None, description="Filter by authors")
    journals: Optional[List[str]] = Field(None, description="Filter by journals/venues")
    min_citations: Optional[int] = Field(None, ge=0, description="Minimum citation count")
    open_access_only: bool = Field(False, description="Only return open access papers")
    sources_filter: Optional[List[str]] = Field(None, description="Filter by specific sources")


class AdvancedSearchResponse(BaseModel):
    """Response model for advanced search."""

    query: str
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    total_found: int
    total_filtered: int
    total_returned: int


class QueryParseRequest(BaseModel):
    """Request model for query parsing."""

    query: str = Field(..., description="Complex query to parse")


class QueryParseResponse(BaseModel):
    """Response model for query parsing."""

    original_query: str
    parsed_query: str
    filters: Dict[str, Any]


router = APIRouter()


@router.post("/advanced-search", response_model=AdvancedSearchResponse)
async def advanced_search_endpoint(req: AdvancedSearchRequest) -> Dict[str, Any]:
    """
    Perform advanced search with semantic capabilities and intelligent filtering.

    This endpoint supports:
    - Semantic search expansion
    - Advanced filtering by date, author, journal, citations
    - Multiple ranking methods
    - Query parsing for complex search strings

    Example queries:
    - "machine learning author:Goodfellow"
    - "neural networks year:2023 journal:Nature"
    - 'deep learning title:"attention is all you need"'
    """
    # Build filters from request
    filters = {}

    if req.date_range_start or req.date_range_end:
        filters["date_range"] = {
            "start": req.date_range_start,
            "end": req.date_range_end
        }

    if req.authors:
        filters["authors"] = req.authors

    if req.journals:
        filters["journals"] = req.journals

    if req.min_citations is not None:
        filters["min_citations"] = req.min_citations

    if req.open_access_only:
        filters["open_access_only"] = req.open_access_only

    if req.sources_filter:
        filters["sources"] = req.sources_filter

    # Perform advanced search
    result = await advanced_search(
        query=req.query,
        sources=req.sources,
        limit=req.limit,
        filters=filters,
        semantic_search=req.semantic_search,
        ranking_method=req.ranking_method
    )

    return result


@router.post("/parse-query", response_model=QueryParseResponse)
async def parse_query_endpoint(req: QueryParseRequest) -> Dict[str, Any]:
    """
    Parse a complex search query into base query and filters.

    Supports field-specific searches like:
    - author:"Ian Goodfellow"
    - journal:Nature year:2023
    - title:"Deep Learning"
    """
    parsed_query, filters = parse_search_query(req.query)

    return {
        "original_query": req.query,
        "parsed_query": parsed_query,
        "filters": filters
    }


@router.get("/search-examples")
async def search_examples() -> Dict[str, List[str]]:
    """
    Get examples of advanced search queries.

    Returns various examples of how to use the advanced search features.
    """
    return {
        "basic_queries": [
            "machine learning",
            "neural networks",
            "climate change"
        ],
        "field_specific_queries": [
            'author:"Ian Goodfellow"',
            "journal:Nature year:2023",
            'title:"Attention Is All You Need"',
            "machine learning author:Hinton"
        ],
        "complex_queries": [
            "deep learning year:2023 min_citations:100",
            "neural networks journal:Science open_access_only:true",
            "artificial intelligence author:Mnih ranking:citations"
        ],
        "semantic_search_examples": [
            "machine learning semantic:true",
            "neural networks semantic:true ranking:date"
        ]
    }


@router.get("/ranking-methods")
async def ranking_methods() -> Dict[str, Dict[str, str]]:
    """
    Get available ranking methods and their descriptions.
    """
    return {
        "relevance": {
            "description": "Rank by relevance score based on title, abstract, and author matches",
            "best_for": "Finding most relevant papers for your research question"
        },
        "date": {
            "description": "Rank by publication date (newest first)",
            "best_for": "Finding the most recent research on a topic"
        },
        "citations": {
            "description": "Rank by citation count (most cited first)",
            "best_for": "Finding influential or highly-cited papers"
        }
    }


@router.get("/filter-options")
async def filter_options() -> Dict[str, Dict[str, Any]]:
    """
    Get available filter options and their parameters.
    """
    return {
        "date_range": {
            "description": "Filter by publication year range",
            "parameters": {
                "start": "Start year (integer, 1900-2030)",
                "end": "End year (integer, 1900-2030)"
            }
        },
        "authors": {
            "description": "Filter by specific authors",
            "parameters": {
                "authors": "List of author names to match"
            }
        },
        "journals": {
            "description": "Filter by specific journals or venues",
            "parameters": {
                "journals": "List of journal names to match"
            }
        },
        "min_citations": {
            "description": "Only return papers with minimum citation count",
            "parameters": {
                "min_citations": "Minimum number of citations (integer >= 0)"
            }
        },
        "open_access_only": {
            "description": "Only return open access papers",
            "parameters": {
                "open_access_only": "Boolean flag"
            }
        },
        "sources": {
            "description": "Filter by specific data sources",
            "parameters": {
                "sources": "List of source names (arxiv, crossref, pubmed, semanticscholar)"
            }
        }
    }
