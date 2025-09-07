"""Advanced paper recommendation system using multiple algorithms."""

import asyncio
from collections import defaultdict, Counter
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta

import numpy as np
from loguru import logger

from ..config import settings
from ..exceptions import SciPaperError
from .fetcher import Fetcher


class PaperRecommendationEngine:
    """Advanced paper recommendation engine using multiple algorithms."""

    def __init__(self):
        self.fetcher = Fetcher()
        self.paper_cache = {}  # Cache for paper metadata
        self.user_profiles = {}  # User reading/interaction history
        self.similarity_cache = {}  # Cache for paper similarity scores

    async def get_recommendations(
        self,
        user_id: Optional[str] = None,
        liked_papers: Optional[List[str]] = None,
        read_papers: Optional[List[str]] = None,
        current_interests: Optional[List[str]] = None,
        limit: int = 10,
        algorithm: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Get personalized paper recommendations using multiple algorithms.

        Args:
            user_id: Unique user identifier for personalized recommendations
            liked_papers: List of papers the user has liked/favorited
            read_papers: List of papers the user has read
            current_interests: Current research interests/topics
            limit: Number of recommendations to return
            algorithm: Recommendation algorithm ("content", "collaborative", "citation", "hybrid")

        Returns:
            Dict containing recommendations and metadata
        """
        try:
            # Build user profile
            user_profile = self._build_user_profile(
                user_id, liked_papers or [], read_papers or [], current_interests or []
            )

            # Get recommendations based on algorithm
            if algorithm == "content":
                recommendations = await self._content_based_recommendations(user_profile, limit)
            elif algorithm == "collaborative":
                recommendations = await self._collaborative_filtering_recommendations(user_profile, limit)
            elif algorithm == "citation":
                recommendations = await self._citation_based_recommendations(user_profile, limit)
            else:  # hybrid
                recommendations = await self._hybrid_recommendations(user_profile, limit)

            # Enrich recommendations with metadata
            enriched_recommendations = await self._enrich_recommendations(recommendations)

            return {
                "recommendations": enriched_recommendations,
                "algorithm_used": algorithm,
                "user_profile": user_profile,
                "generated_at": datetime.now().isoformat(),
                "total_candidates": len(recommendations)
            }

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise SciPaperError(f"Recommendation generation failed: {e}")

    def _build_user_profile(
        self,
        user_id: Optional[str],
        liked_papers: List[str],
        read_papers: List[str],
        interests: List[str]
    ) -> Dict[str, Any]:
        """Build a comprehensive user profile for recommendations."""
        profile = {
            "user_id": user_id,
            "liked_papers": liked_papers,
            "read_papers": read_papers,
            "interests": interests,
            "preferred_sources": [],
            "preferred_authors": [],
            "preferred_journals": [],
            "preferred_topics": [],
            "temporal_preferences": {},
            "citation_preferences": {}
        }

        # Analyze liked and read papers for patterns
        all_papers = liked_papers + read_papers
        if all_papers:
            paper_metadata = []
            for paper_id in all_papers[:20]:  # Limit for performance
                if paper_id in self.paper_cache:
                    paper_metadata.append(self.paper_cache[paper_id])

            if paper_metadata:
                # Extract preferred sources
                sources = [p.get("source") for p in paper_metadata if p.get("source")]
                profile["preferred_sources"] = [s for s, _ in Counter(sources).most_common(3)]

                # Extract preferred authors
                authors = []
                for p in paper_metadata:
                    authors.extend(p.get("authors", []))
                profile["preferred_authors"] = [a for a, _ in Counter(authors).most_common(5)]

                # Extract preferred journals
                journals = [p.get("journal") for p in paper_metadata if p.get("journal")]
                profile["preferred_journals"] = [j for j, _ in Counter(journals).most_common(3)]

                # Extract temporal patterns
                years = [p.get("date") for p in paper_metadata if p.get("date")]
                if years:
                    profile["temporal_preferences"] = {
                        "avg_year": sum(int(y) for y in years if y.isdigit()) / len(years),
                        "year_range": f"{min(years)}-{max(years)}"
                    }

        # Add interest-based topics
        profile["preferred_topics"] = interests

        return profile

    async def _content_based_recommendations(
        self,
        user_profile: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate content-based recommendations."""
        recommendations = []

        # Use user's interests and preferred topics
        search_terms = user_profile.get("interests", []) + user_profile.get("preferred_topics", [])

        if not search_terms:
            return recommendations

        # Search for papers related to user's interests
        for term in search_terms[:3]:  # Limit to top 3 interests
            try:
                results = await self.fetcher.search(term, limit=limit * 2)

                # Score and rank results
                for paper in results:
                    score = self._calculate_content_score(paper, user_profile)
                    paper["recommendation_score"] = score
                    paper["recommendation_reason"] = f"Related to interest: {term}"

                recommendations.extend(results)
            except Exception as e:
                logger.warning(f"Content-based search failed for term '{term}': {e}")

        # Remove duplicates and sort by score
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            paper_id = rec.get("id")
            if paper_id and paper_id not in seen:
                seen.add(paper_id)
                unique_recommendations.append(rec)

        return sorted(unique_recommendations, key=lambda x: x.get("recommendation_score", 0), reverse=True)[:limit]

    async def _collaborative_filtering_recommendations(
        self,
        user_profile: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate collaborative filtering recommendations."""
        # This is a simplified version - in production, you'd use a full CF algorithm
        recommendations = []

        # Find similar users based on liked papers
        liked_papers = user_profile.get("liked_papers", [])
        if not liked_papers:
            return recommendations

        # Get papers that cite or are cited by liked papers
        related_papers = set()
        for paper_id in liked_papers[:5]:  # Limit for performance
            try:
                # This would typically query a citation database
                # For now, we'll use a simple approach
                paper_data = await self._get_paper_data(paper_id)
                if paper_data:
                    # Add papers by same authors
                    authors = paper_data.get("authors", [])
                    for author in authors[:2]:  # Limit authors
                        author_papers = await self.fetcher.search(f'author:"{author}"', limit=5)
                        related_papers.update(p["id"] for p in author_papers if p.get("id") != paper_id)

            except Exception as e:
                logger.warning(f"Failed to get related papers for {paper_id}: {e}")

        # Convert to recommendations
        for paper_id in list(related_papers)[:limit]:
            try:
                paper_data = await self._get_paper_data(paper_id)
                if paper_data:
                    paper_data["recommendation_score"] = 0.8  # High confidence for collaborative filtering
                    paper_data["recommendation_reason"] = "Similar users liked this paper"
                    recommendations.append(paper_data)
            except Exception as e:
                logger.warning(f"Failed to get paper data for {paper_id}: {e}")

        return recommendations

    async def _citation_based_recommendations(
        self,
        user_profile: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate citation-based recommendations."""
        recommendations = []

        # Get papers that are frequently cited by papers the user likes
        liked_papers = user_profile.get("liked_papers", [])
        if not liked_papers:
            return recommendations

        citation_candidates = set()

        for paper_id in liked_papers[:3]:  # Limit for performance
            try:
                # Get papers that cite this paper (would need citation API)
                # For now, use a simplified approach
                paper_data = await self._get_paper_data(paper_id)
                if paper_data:
                    # Find papers in the same field/area
                    journal = paper_data.get("journal", "")
                    if journal:
                        related_papers = await self.fetcher.search(f'journal:"{journal}"', limit=10)
                        citation_candidates.update(p["id"] for p in related_papers if p.get("id") != paper_id)

            except Exception as e:
                logger.warning(f"Citation analysis failed for {paper_id}: {e}")

        # Convert to recommendations
        for paper_id in list(citation_candidates)[:limit]:
            try:
                paper_data = await self._get_paper_data(paper_id)
                if paper_data:
                    paper_data["recommendation_score"] = 0.7
                    paper_data["recommendation_reason"] = "Frequently cited in your field"
                    recommendations.append(paper_data)
            except Exception as e:
                logger.warning(f"Failed to get paper data for {paper_id}: {e}")

        return recommendations

    async def _hybrid_recommendations(
        self,
        user_profile: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate hybrid recommendations combining multiple algorithms."""
        # Get recommendations from different algorithms
        content_rec = await self._content_based_recommendations(user_profile, limit * 2)
        collab_rec = await self._collaborative_filtering_recommendations(user_profile, limit * 2)
        citation_rec = await self._citation_based_recommendations(user_profile, limit * 2)

        # Combine and deduplicate
        all_recommendations = content_rec + collab_rec + citation_rec

        # Remove duplicates and adjust scores
        seen = {}
        for rec in all_recommendations:
            paper_id = rec.get("id")
            if paper_id:
                if paper_id in seen:
                    # Average the scores if duplicate
                    existing = seen[paper_id]
                    existing["recommendation_score"] = (
                        existing.get("recommendation_score", 0) + rec.get("recommendation_score", 0)
                    ) / 2
                    existing["recommendation_reason"] += f"; {rec.get('recommendation_reason', '')}"
                else:
                    seen[paper_id] = rec

        # Sort by combined score
        final_recommendations = list(seen.values())
        final_recommendations.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)

        return final_recommendations[:limit]

    def _calculate_content_score(self, paper: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate content-based similarity score."""
        score = 0.0

        # Interest matching
        interests = user_profile.get("interests", [])
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()

        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in title:
                score += 3.0
            if interest_lower in abstract:
                score += 2.0

        # Author matching
        preferred_authors = user_profile.get("preferred_authors", [])
        paper_authors = paper.get("authors", [])

        for author in paper_authors:
            if any(pref_author.lower() in author.lower() for pref_author in preferred_authors):
                score += 2.0

        # Journal matching
        preferred_journals = user_profile.get("preferred_journals", [])
        journal = paper.get("journal", "")

        if any(pref_journal.lower() in journal.lower() for pref_journal in preferred_journals):
            score += 1.5

        # Recency bonus
        temporal_prefs = user_profile.get("temporal_preferences", {})
        avg_year = temporal_prefs.get("avg_year")
        if avg_year:
            try:
                paper_year = int(paper.get("date", "2000"))
                year_diff = abs(paper_year - avg_year)
                recency_score = max(0, 2.0 - year_diff * 0.1)
                score += recency_score
            except (ValueError, TypeError):
                pass

        # Citation bonus
        citations = paper.get("citation_count", 0)
        if citations > 0:
            citation_score = min(citations / 100, 2.0)  # Cap at 2.0
            score += citation_score

        return score

    async def _get_paper_data(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get paper data, using cache when possible."""
        if paper_id in self.paper_cache:
            return self.paper_cache[paper_id]

        try:
            paper_data = await self.fetcher.fetch(paper_id)
            if paper_data:
                self.paper_cache[paper_id] = paper_data
            return paper_data
        except Exception as e:
            logger.warning(f"Failed to fetch paper {paper_id}: {e}")
            return None

    async def _enrich_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich recommendations with additional metadata."""
        enriched = []

        for rec in recommendations:
            enriched_rec = rec.copy()

            # Add recommendation metadata
            enriched_rec["recommended_at"] = datetime.now().isoformat()
            enriched_rec["recommendation_confidence"] = min(rec.get("recommendation_score", 0) / 10, 1.0)

            # Add diversity score (how different this is from other recommendations)
            enriched_rec["diversity_score"] = self._calculate_diversity_score(rec, recommendations)

            enriched.append(enriched_rec)

        return enriched

    def _calculate_diversity_score(self, paper: Dict[str, Any], all_papers: List[Dict[str, Any]]) -> float:
        """Calculate how diverse this paper is compared to others."""
        if len(all_papers) <= 1:
            return 1.0

        # Simple diversity based on different authors/journals
        paper_authors = set(paper.get("authors", []))
        paper_journal = paper.get("journal", "")

        diversity_scores = []
        for other_paper in all_papers:
            if other_paper.get("id") == paper.get("id"):
                continue

            other_authors = set(other_paper.get("authors", []))
            other_journal = other_paper.get("journal", "")

            # Calculate overlap
            author_overlap = len(paper_authors & other_authors) if paper_authors and other_authors else 0
            journal_overlap = 1 if paper_journal == other_journal and paper_journal else 0

            # Lower overlap = higher diversity
            overlap_score = (author_overlap + journal_overlap) / 2
            diversity_scores.append(1 - overlap_score)

        return sum(diversity_scores) / len(diversity_scores) if diversity_scores else 1.0


class RecommendationEvaluator:
    """Evaluate recommendation quality and user satisfaction."""

    def __init__(self):
        self.metrics = defaultdict(list)

    def evaluate_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        user_feedback: Optional[List[bool]] = None
    ) -> Dict[str, Any]:
        """Evaluate recommendation quality."""
        if not recommendations:
            return {"error": "No recommendations to evaluate"}

        metrics = {
            "total_recommendations": len(recommendations),
            "avg_recommendation_score": sum(r.get("recommendation_score", 0) for r in recommendations) / len(recommendations),
            "avg_confidence": sum(r.get("recommendation_confidence", 0) for r in recommendations) / len(recommendations),
            "avg_diversity": sum(r.get("diversity_score", 0) for r in recommendations) / len(recommendations),
            "score_distribution": self._calculate_score_distribution(recommendations)
        }

        if user_feedback:
            metrics["user_satisfaction"] = sum(user_feedback) / len(user_feedback)

        return metrics

    def _calculate_score_distribution(self, recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of recommendation scores."""
        distribution = {"high": 0, "medium": 0, "low": 0}

        for rec in recommendations:
            score = rec.get("recommendation_score", 0)
            if score >= 7:
                distribution["high"] += 1
            elif score >= 4:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1

        return distribution


# Convenience functions
async def get_paper_recommendations(**kwargs) -> Dict[str, Any]:
    """Convenience function for getting paper recommendations."""
    engine = PaperRecommendationEngine()
    return await engine.get_recommendations(**kwargs)

def evaluate_recommendations(recommendations: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """Convenience function for evaluating recommendations."""
    evaluator = RecommendationEvaluator()
    return evaluator.evaluate_recommendations(recommendations, **kwargs)
