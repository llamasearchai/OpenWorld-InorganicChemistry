"""Advanced search functionality with semantic search and intelligent filtering."""

import asyncio
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from loguru import logger

from ..config import settings
from ..exceptions import SciPaperError
from .fetcher import Fetcher


class AdvancedSearchEngine:
    """Advanced search engine with semantic capabilities and intelligent filtering."""

    def __init__(self):
        self.fetcher = Fetcher()
        self.semantic_cache = {}  # Cache for semantic search results

    async def advanced_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        semantic_search: bool = False,
        ranking_method: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple strategies and intelligent filtering.

        Args:
            query: Search query
            sources: List of sources to search
            limit: Maximum results to return
            filters: Advanced filters (date_range, authors, journals, etc.)
            semantic_search: Whether to use semantic search
            ranking_method: How to rank results ("relevance", "date", "citations")

        Returns:
            Dict containing search results and metadata
        """
        try:
            # Parse and expand query
            expanded_queries = self._expand_query(query, semantic_search)

            # Search across all sources with expanded queries
            all_results = []
            source_stats = defaultdict(int)

            for expanded_query in expanded_queries:
                for source in (sources or self.fetcher.available_sources):
                    try:
                        results = await self.fetcher.search(
                            expanded_query, [source], limit * 2  # Get more for filtering
                        )
                        all_results.extend(results)
                        source_stats[source] += len(results)
                        logger.info(f"Found {len(results)} results from {source} for query: {expanded_query}")
                    except Exception as e:
                        logger.warning(f"Search failed for {source}: {e}")
                        continue

            # Remove duplicates
            unique_results = self._deduplicate_results(all_results)

            # Apply advanced filters
            if filters:
                filtered_results = self._apply_filters(unique_results, filters)
            else:
                filtered_results = unique_results

            # Rank and sort results
            ranked_results = self._rank_results(filtered_results, ranking_method, query)

            # Limit results
            final_results = ranked_results[:limit]

            # Generate search metadata
            metadata = self._generate_search_metadata(
                query, expanded_queries, source_stats, len(final_results), filters
            )

            return {
                "query": query,
                "results": final_results,
                "metadata": metadata,
                "total_found": len(unique_results),
                "total_filtered": len(filtered_results),
                "total_returned": len(final_results)
            }

        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            raise SciPaperError(f"Advanced search failed: {e}")

    def _expand_query(self, query: str, semantic_search: bool = False) -> List[str]:
        """Expand query with synonyms, related terms, and semantic variations."""
        expanded_queries = [query]

        if not semantic_search:
            return expanded_queries

        # Basic query expansion (can be enhanced with NLP models)
        expansions = []

        # Add common variations
        if "machine learning" in query.lower():
            expansions.extend([
                query.replace("machine learning", "ML"),
                query.replace("machine learning", "artificial intelligence"),
                query.replace("machine learning", "neural networks")
            ])

        if "neural network" in query.lower():
            expansions.extend([
                query.replace("neural network", "deep learning"),
                query.replace("neural network", "neural net"),
                query.replace("neural network", "ANN")
            ])

        if "climate change" in query.lower():
            expansions.extend([
                query.replace("climate change", "global warming"),
                query.replace("climate change", "climate crisis")
            ])

        # Add year-based expansions for recent research
        if not any(char.isdigit() for char in query):
            current_year = 2024
            expansions.append(f"{query} {current_year}")
            expansions.append(f"{query} {current_year-1}")

        expanded_queries.extend(expansions[:3])  # Limit to 3 expansions

        return list(set(expanded_queries))  # Remove duplicates

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on DOI, title similarity, and other factors."""
        seen = set()
        unique_results = []

        for result in results:
            # Create a unique identifier
            doi = result.get("doi", "").strip().lower()
            title = result.get("title", "").strip().lower()[:50]  # First 50 chars
            authors = " ".join(result.get("authors", [])).strip().lower()[:30]

            # Use DOI if available, otherwise use title+authors
            if doi:
                identifier = doi
            else:
                identifier = f"{title}|{authors}"

            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)

        return unique_results

    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply advanced filters to search results."""
        filtered_results = results

        # Date range filter
        if "date_range" in filters:
            date_range = filters["date_range"]
            if isinstance(date_range, dict):
                start_year = date_range.get("start")
                end_year = date_range.get("end")

                filtered_results = [
                    r for r in filtered_results
                    if self._matches_date_range(r.get("date", ""), start_year, end_year)
                ]

        # Author filter
        if "authors" in filters:
            author_filter = filters["authors"]
            if isinstance(author_filter, list):
                filtered_results = [
                    r for r in filtered_results
                    if any(self._matches_author(r.get("authors", []), author)
                          for author in author_filter)
                ]

        # Journal/Venue filter
        if "journals" in filters:
            journal_filter = filters["journals"]
            if isinstance(journal_filter, list):
                filtered_results = [
                    r for r in filtered_results
                    if any(journal.lower() in r.get("journal", "").lower()
                          for journal in journal_filter)
                ]

        # Citation count filter
        if "min_citations" in filters:
            min_citations = filters["min_citations"]
            filtered_results = [
                r for r in filtered_results
                if (r.get("citation_count", 0) or 0) >= min_citations
            ]

        # Open access filter
        if "open_access_only" in filters and filters["open_access_only"]:
            filtered_results = [
                r for r in filtered_results
                if r.get("url", "").endswith((".pdf", ".PDF")) or
                "openaccess" in r.get("url", "").lower()
            ]

        # Source filter
        if "sources" in filters:
            source_filter = filters["sources"]
            if isinstance(source_filter, list):
                filtered_results = [
                    r for r in filtered_results
                    if r.get("source", "") in source_filter
                ]

        return filtered_results

    def _matches_date_range(self, date_str: str, start_year: Optional[int],
                           end_year: Optional[int]) -> bool:
        """Check if a date string falls within the specified year range."""
        if not date_str:
            return True  # Include if no date available

        try:
            year = int(date_str)
            if start_year and year < start_year:
                return False
            if end_year and year > end_year:
                return False
            return True
        except (ValueError, TypeError):
            return True  # Include if date parsing fails

    def _matches_author(self, authors: List[str], target_author: str) -> bool:
        """Check if target author matches any of the paper's authors."""
        target_lower = target_author.lower()
        return any(target_lower in author.lower() for author in authors)

    def _rank_results(self, results: List[Dict[str, Any]], method: str,
                     original_query: str) -> List[Dict[str, Any]]:
        """Rank and sort search results based on the specified method."""

        def calculate_relevance_score(result: Dict[str, Any]) -> float:
            """Calculate relevance score based on various factors."""
            score = 0.0

            # Title relevance (highest weight)
            title = result.get("title", "").lower()
            query_terms = set(original_query.lower().split())
            title_matches = sum(1 for term in query_terms if term in title)
            score += title_matches * 10

            # Abstract relevance
            abstract = result.get("abstract", "").lower()
            abstract_matches = sum(1 for term in query_terms if term in abstract)
            score += abstract_matches * 5

            # Author name relevance
            authors = " ".join(result.get("authors", [])).lower()
            author_matches = sum(1 for term in query_terms if term in authors)
            score += author_matches * 3

            # Citation count (logarithmic scaling)
            citations = result.get("citation_count", 0) or 0
            if citations > 0:
                score += min(citations ** 0.5, 20)  # Cap at 20 points

            # Recency bonus (newer papers get slight boost)
            try:
                year = int(result.get("date", "2000"))
                years_old = 2024 - year
                recency_score = max(0, 5 - years_old * 0.5)
                score += recency_score
            except (ValueError, TypeError):
                pass

            return score

        if method == "relevance":
            # Sort by relevance score (descending)
            results_with_scores = [
                (result, calculate_relevance_score(result)) for result in results
            ]
            results_with_scores.sort(key=lambda x: x[1], reverse=True)
            return [result for result, _ in results_with_scores]

        elif method == "date":
            # Sort by date (newest first)
            def sort_key(result):
                try:
                    return int(result.get("date", "0"))
                except (ValueError, TypeError):
                    return 0
            return sorted(results, key=sort_key, reverse=True)

        elif method == "citations":
            # Sort by citation count (highest first)
            def sort_key(result):
                return result.get("citation_count", 0) or 0
            return sorted(results, key=sort_key, reverse=True)

        else:
            # Default to relevance
            return self._rank_results(results, "relevance", original_query)

    def _generate_search_metadata(
        self,
        original_query: str,
        expanded_queries: List[str],
        source_stats: Dict[str, int],
        result_count: int,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive search metadata."""
        return {
            "original_query": original_query,
            "expanded_queries": expanded_queries,
            "query_expansion_used": len(expanded_queries) > 1,
            "sources_searched": list(source_stats.keys()),
            "source_results": dict(source_stats),
            "total_results_found": sum(source_stats.values()),
            "results_returned": result_count,
            "filters_applied": filters or {},
            "search_timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "search_engine_version": "2.0.0"
        }


class SearchQueryParser:
    """Parse and understand complex search queries."""

    def __init__(self):
        self.field_patterns = {
            "author": re.compile(r'author:"([^"]+)"|author:(\S+)'),
            "journal": re.compile(r'journal:"([^"]+)"|journal:(\S+)'),
            "year": re.compile(r'year:(\d{4})'),
            "doi": re.compile(r'doi:(\S+)'),
            "title": re.compile(r'title:"([^"]+)"'),
        }

    def parse_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse a complex query into base query and filters.

        Examples:
        - "machine learning author:Goodfellow"
        - "neural networks year:2023 journal:Nature"
        - 'deep learning title:"attention is all you need"'
        """
        filters = {}
        clean_query = query

        # Extract field-specific filters
        for field, pattern in self.field_patterns.items():
            matches = pattern.findall(clean_query)
            if matches:
                if field in ["author", "journal", "title"]:
                    # Handle quoted and unquoted versions
                    values = []
                    for match in matches:
                        values.extend([m for m in match if m])  # Remove empty strings
                    if values:
                        filters[field] = values
                elif field == "year":
                    years = [int(match) for match in matches]
                    if years:
                        filters["date_range"] = {"start": min(years), "end": max(years)}
                elif field == "doi":
                    filters["doi"] = matches

                # Remove the field specification from the query
                clean_query = pattern.sub("", clean_query).strip()

        # Clean up extra whitespace and operators
        clean_query = re.sub(r'\s+', ' ', clean_query).strip()
        clean_query = re.sub(r'^\s*(AND|OR|NOT)\s+', '', clean_query)
        clean_query = re.sub(r'\s+(AND|OR|NOT)\s*$', '', clean_query)

        return clean_query, filters


# Convenience functions
async def advanced_search(**kwargs) -> Dict[str, Any]:
    """Convenience function for advanced search."""
    engine = AdvancedSearchEngine()
    return await engine.advanced_search(**kwargs)

def parse_search_query(query: str) -> Tuple[str, Dict[str, Any]]:
    """Convenience function for parsing search queries."""
    parser = SearchQueryParser()
    return parser.parse_query(query)
