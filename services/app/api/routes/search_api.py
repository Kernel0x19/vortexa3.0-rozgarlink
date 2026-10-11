"""Semantic Vector Search API Routes

This module provides natural language opportunity search endpoints backed by pgvector similarity matching.

Satisfies Requirements: 15.1, 15.5, 15.6, 15.7
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.db.session import get_db
from app.intelligence.vector_search import VectorSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Semantic Search"])


def infer_category(query: str) -> Optional[str]:
    """Restrict unfiltered searches when the user explicitly names a category."""
    text = query.lower()
    keywords = {
        "scholarship": ("scholarship", "scholarships", "fellowship", "grant"),
        "internship": ("internship", "internships", "intern", "trainee"),
        "placement": ("placement", "placements", "campus job"),
        "hackathon": ("hackathon", "hackathons"),
    }
    for category, terms in keywords.items():
        if any(term in text for term in terms):
            return category
    return None


@router.get("/opportunities")
async def search_opportunities_semantic(
    q: str = Query(..., min_length=1, description="Natural language search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    top_k: int = Query(20, ge=1, le=100, description="Max results"),
    min_score: float = Query(0.10, ge=-1.0, le=1.0, description="Minimum relevance score"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Execute semantic vector similarity search over opportunities."""
    # The UI's default is "All", but a query such as "scholarships for SC
    # students" should not return internships just because no filter was clicked.
    effective_category = category or infer_category(q)
    search_service = VectorSearchService(db)
    # SQLAlchemy and embedding generation are synchronous CPU/IO work. Run
    # them outside the event loop so one slow search does not freeze health
    # checks or every other API request.
    results = await run_in_threadpool(
        lambda: asyncio.run(search_service.search_opportunities(
            query=q,
            category=effective_category,
            top_k=top_k,
            min_score=min_score,
        ))
    )
    return {
        "query": q,
        "category": effective_category,
        "results_count": len(results),
        "matches": results
    }
