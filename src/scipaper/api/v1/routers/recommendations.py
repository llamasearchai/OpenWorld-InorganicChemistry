"""Paper recommendations API endpoint."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ....core.recommendations import get_paper_recommendations, evaluate_recommendations


class RecommendationRequest(BaseModel):
    """Request model for paper recommendations."""

    user_id: Optional[str] = Field(None, description="Unique user identifier")
    liked_papers: Optional[List[str]] = Field(None, description="Papers the user has liked/favorited")
    read_papers: Optional[List[str]] = Field(None, description="Papers the user has read")
    current_interests: Optional[List[str]] = Field(None, description="Current research interests")
    limit: int = Field(10, ge=1, le=50, description="Number of recommendations to return")
    algorithm: str = Field("hybrid", description="Recommendation algorithm",
                          regex="^(content|collaborative|citation|hybrid)$")


class RecommendationResponse(BaseModel):
    """Response model for paper recommendations."""

    recommendations: List[Dict[str, Any]]
    algorithm_used: str
    user_profile: Dict[str, Any]
    generated_at: str
    total_candidates: int


class EvaluationRequest(BaseModel):
    """Request model for recommendation evaluation."""

    recommendations: List[Dict[str, Any]] = Field(..., description="Recommendations to evaluate")
    user_feedback: Optional[List[bool]] = Field(None, description="User feedback (liked/disliked)")


class EvaluationResponse(BaseModel):
    """Response model for recommendation evaluation."""

    total_recommendations: int
    avg_recommendation_score: float
    avg_confidence: float
    avg_diversity: float
    score_distribution: Dict[str, int]
    user_satisfaction: Optional[float] = None


router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations_endpoint(req: RecommendationRequest) -> Dict[str, Any]:
    """
    Get personalized paper recommendations using advanced algorithms.

    This endpoint supports multiple recommendation algorithms:
    - **content**: Based on user's interests and reading history
    - **collaborative**: Based on similar users' preferences
    - **citation**: Based on citation networks and field relevance
    - **hybrid**: Combines all algorithms for best results

    The system analyzes user profiles, reading patterns, and research interests
    to provide highly relevant paper recommendations.
    """
    result = await get_paper_recommendations(
        user_id=req.user_id,
        liked_papers=req.liked_papers,
        read_papers=req.read_papers,
        current_interests=req.current_interests,
        limit=req.limit,
        algorithm=req.algorithm
    )

    return result


@router.post("/recommendations/evaluate", response_model=EvaluationResponse)
async def evaluate_recommendations_endpoint(req: EvaluationRequest) -> Dict[str, Any]:
    """
    Evaluate the quality of recommendations.

    This endpoint analyzes recommendation quality metrics including:
    - Average recommendation scores
    - Confidence levels
    - Diversity of recommendations
    - User satisfaction rates
    """
    result = evaluate_recommendations(
        recommendations=req.recommendations,
        user_feedback=req.user_feedback
    )

    return result


@router.get("/recommendations/algorithms")
async def recommendation_algorithms() -> Dict[str, Dict[str, str]]:
    """
    Get information about available recommendation algorithms.
    """
    return {
        "content": {
            "name": "Content-Based Filtering",
            "description": "Recommends papers similar to user's interests and reading history",
            "best_for": "Users with specific research interests",
            "strengths": "Personalized, interpretable recommendations"
        },
        "collaborative": {
            "name": "Collaborative Filtering",
            "description": "Recommends papers liked by similar users",
            "best_for": "Discovering papers outside your usual interests",
            "strengths": "Serendipitous discoveries, social proof"
        },
        "citation": {
            "name": "Citation-Based",
            "description": "Recommends papers frequently cited in your field",
            "best_for": "Staying current with influential research",
            "strengths": "High-quality, field-relevant papers"
        },
        "hybrid": {
            "name": "Hybrid Approach",
            "description": "Combines all algorithms for optimal recommendations",
            "best_for": "Best overall recommendation quality",
            "strengths": "Balanced, high-confidence recommendations"
        }
    }


@router.get("/recommendations/examples")
async def recommendation_examples() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get examples of how to use the recommendation system.
    """
    return {
        "basic_usage": [
            {
                "description": "Get recommendations based on interests",
                "request": {
                    "current_interests": ["machine learning", "neural networks"],
                    "limit": 10,
                    "algorithm": "content"
                }
            },
            {
                "description": "Get recommendations for existing user",
                "request": {
                    "user_id": "researcher123",
                    "liked_papers": ["10.1000/test1", "10.1000/test2"],
                    "algorithm": "hybrid"
                }
            }
        ],
        "advanced_usage": [
            {
                "description": "Field-specific recommendations",
                "request": {
                    "current_interests": ["quantum computing", "cryptography"],
                    "read_papers": ["10.1000/quantum1", "10.1000/crypto1"],
                    "limit": 15,
                    "algorithm": "citation"
                }
            },
            {
                "description": "Cross-disciplinary recommendations",
                "request": {
                    "liked_papers": ["10.1000/cs1", "10.1000/bio1"],
                    "algorithm": "collaborative"
                }
            }
        ],
        "evaluation_examples": [
            {
                "description": "Evaluate recommendation quality",
                "request": {
                    "recommendations": [
                        {"id": "10.1000/test1", "recommendation_score": 8.5},
                        {"id": "10.1000/test2", "recommendation_score": 7.2}
                    ],
                    "user_feedback": [True, False]
                }
            }
        ]
    }


@router.get("/recommendations/metrics")
async def recommendation_metrics() -> Dict[str, Dict[str, Any]]:
    """
    Get information about recommendation quality metrics.
    """
    return {
        "recommendation_score": {
            "description": "Overall recommendation quality score (0-10)",
            "interpretation": {
                "9-10": "Excellent recommendation",
                "7-8.9": "Good recommendation",
                "5-6.9": "Fair recommendation",
                "0-4.9": "Poor recommendation"
            }
        },
        "confidence": {
            "description": "System confidence in the recommendation (0-1)",
            "interpretation": {
                "0.8-1.0": "Very confident",
                "0.6-0.79": "Confident",
                "0.4-0.59": "Moderately confident",
                "0.0-0.39": "Low confidence"
            }
        },
        "diversity_score": {
            "description": "How diverse this recommendation is from others (0-1)",
            "interpretation": {
                "0.8-1.0": "Very diverse",
                "0.6-0.79": "Diverse",
                "0.4-0.59": "Moderately diverse",
                "0.0-0.39": "Similar to others"
            }
        },
        "user_satisfaction": {
            "description": "Percentage of recommendations liked by users",
            "target": "Aim for >70% satisfaction rate"
        }
    }


@router.post("/recommendations/feedback")
async def submit_feedback(
    user_id: str = Query(..., description="User identifier"),
    paper_id: str = Query(..., description="Paper identifier"),
    liked: bool = Query(..., description="Whether the user liked this recommendation"),
    feedback_text: Optional[str] = Query(None, description="Optional feedback text")
) -> Dict[str, str]:
    """
    Submit user feedback on recommendations.

    This helps improve the recommendation algorithm over time.
    """
    # In a real implementation, this would store feedback in a database
    # For now, we'll just acknowledge the feedback

    feedback_type = "positive" if liked else "negative"
    response_message = f"Thank you for your {feedback_type} feedback on paper {paper_id}"

    if feedback_text:
        response_message += f". Additional feedback noted: {feedback_text}"

    return {
        "message": response_message,
        "feedback_recorded": True,
        "user_id": user_id,
        "paper_id": paper_id,
        "feedback_type": feedback_type
    }
