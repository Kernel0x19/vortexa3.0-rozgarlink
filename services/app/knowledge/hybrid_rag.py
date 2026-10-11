import hashlib
import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.db.models import Opportunity, StudentProfile
from app.intelligence.eligibility import evaluate_eligibility

logger = logging.getLogger(__name__)
settings = get_settings()


class HybridRAG:
    """Structured DB (SQLAlchemy) + ChromaDB vector store for semantic search."""

    COLLECTION = "opportunities"

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def _doc_text(self, opp: Opportunity) -> str:
        """Build a rich text representation for vector indexing.

        Including structured fields (amounts, income limit, categories, gender,
        streams, documents) lets the retriever match queries such as
        "scholarship for income below 2.5 lakh" or "documents required"
        that would otherwise miss purely description-based embeddings.
        """
        parts = [opp.title, opp.description or ""]

        # --- Structured amount info ---
        if opp.amount_min or opp.amount_max:
            lo = f"\u20b9{opp.amount_min:,}" if opp.amount_min else ""
            hi = f"\u20b9{opp.amount_max:,}" if opp.amount_max else ""
            if lo and hi:
                parts.append(f"Amount: {lo}\u2013{hi} per annum")
            elif hi:
                parts.append(f"Amount: up to {hi} per annum")
            elif lo:
                parts.append(f"Amount: {lo} per annum")

        # --- Eligibility rules flattened ---
        rules = opp.eligibility_rules
        if rules and isinstance(rules, dict):
            if rules.get("category"):
                parts.append(f"Eligible categories: {', '.join(str(c) for c in rules['category'])}")
            if rules.get("gender"):
                parts.append(f"Gender: {', '.join(str(g) for g in rules['gender'])}")
            if rules.get("streams"):
                parts.append(f"Streams: {', '.join(str(s) for s in rules['streams'])}")
            if rules.get("max_income"):
                parts.append(f"Income limit: \u20b9{rules['max_income']:,} per annum")
            if rules.get("level"):
                parts.append(f"Level: {', '.join(str(l) for l in rules['level'])}")
            if rules.get("institution_type"):
                parts.append(f"Institution: {', '.join(str(i) for i in rules['institution_type'])}")
        elif rules:
            parts.append(str(rules))

        # --- Documents required ---
        if opp.documents_required:
            parts.append(f"Documents required: {', '.join(opp.documents_required)}")

        # --- Tags ---
        if opp.tags:
            parts.append(" ".join(opp.tags))

        return " ".join(parts)

    def _embedding_id(self, opp: Opportunity) -> str:
        return hashlib.sha256(f"{opp.source}:{opp.external_id}".encode()).hexdigest()[:32]

    def index_opportunity(self, opp: Opportunity) -> str:
        doc_id = self._embedding_id(opp)
        text = self._doc_text(opp)
        self._collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[
                {
                    "opportunity_id": opp.id,
                    "source": opp.source,
                    "category": opp.category.value if opp.category else "scholarship",
                    "title": opp.title[:200],
                }
            ],
        )
        opp.embedding_id = doc_id
        return doc_id

    def semantic_search(self, query: str, limit: int = 20, category: str | None = None) -> list[dict[str, Any]]:
        """Enhanced semantic search with natural query processing and balanced filtering."""
        # Enhanced query processing
        processed_query = self._enhance_query_advanced(query)
        
        where = {"category": category} if category else None
        try:
            # Search reasonable pool
            search_limit = min(limit * 2, 40)
            results = self._collection.query(
                query_texts=[processed_query],
                n_results=search_limit,
                where=where,
            )
        except Exception:
            results = self._collection.query(query_texts=[processed_query], n_results=search_limit)

        items = []
        if results and results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0.0
                score = max(0.0, 1.0 - distance)
                
                # Relaxed relevance filtering for better recall
                if score < 0.2:  # Only filter out very low relevance results
                    continue
                    
                items.append({
                    "embedding_id": doc_id,
                    "opportunity_id": meta.get("opportunity_id"),
                    "score": score,
                    "title": meta.get("title"),
                })
        
        # Sort by relevance
        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:limit]
    
    def _enhance_query_advanced(self, query: str) -> str:
        """Advanced query enhancement with contextual expansion and synonym handling."""
        enhanced_query = query.lower()
        
        # Domain-specific query enhancement with more comprehensive mappings
        query_enhancements = {
            "scholarship": "scholarship financial aid education grant stipend funding assistance",
            "internship": "internship training program work experience placement opportunity",
            "engineering": "engineering technical computer science mechanical electrical civil electronics",
            "medical": "medical medicine healthcare doctor nurse pharma biotechnology",
            "sc st": "scheduled caste scheduled tribe reservation category backward",
            "obc": "other backward class reservation category minority",
            "income": "family annual salary earnings financial background economic",
            "documents": "certificate required application form documentation proof",
            "deadline": "last date application deadline submission timeline",
            "eligibility": "eligible criteria requirements qualification conditions",
            "amount": "money funding financial assistance stipend grant value",
        }
        
        # Apply enhancements based on exact keyword matches
        for keyword, enhancement in query_enhancements.items():
            if keyword in enhanced_query:
                enhanced_query += " " + enhancement
        
        # Handle specific program identifiers
        program_identifiers = {
            "aicte": "all india council technical education engineering scholarship",
            "ugc": "university grants commission higher education scholarship",
            "inspire": "innovation science pursuit research scholarship dst",
            "nmms": "national means merit scholarship examination",
        }
        
        for program, expansion in program_identifiers.items():
            if program in enhanced_query:
                enhanced_query += " " + expansion
        
        return enhanced_query

    def reindex_all(self, db) -> int:
        count = 0
        for opp in db.query(Opportunity).filter_by(is_active=True).all():
            self.index_opportunity(opp)
            count += 1
        db.commit()
        return count

    def retrieve_for_profile(self, db, query: str, profile: StudentProfile | None, limit: int = 8) -> list[dict[str, Any]]:
        """Retrieve semantically relevant opportunities with natural filtering."""
        # Use larger candidate pool for better coverage
        candidates = self.semantic_search(query, limit=max(limit * 3, 20), category="scholarship")
        ids = [item["opportunity_id"] for item in candidates if item.get("opportunity_id")]
        opportunities = {
            opp.id: opp for opp in db.query(Opportunity).filter(
                Opportunity.id.in_(ids), Opportunity.is_active.is_(True)
            ).all()
        } if ids else {}
        
        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            opportunity = opportunities.get(candidate.get("opportunity_id"))
            if not opportunity:
                continue
                
            eligibility = evaluate_eligibility(profile, opportunity.eligibility_rules or {})
            if not eligibility["eligible"]:
                continue
            
            # Balanced relevance scoring
            semantic_score = candidate["score"]
            query_specific_score = self._calculate_query_specific_score_enhanced(query, opportunity)
            combined_relevance = (semantic_score * 0.7) + (query_specific_score * 0.3)
            
            ranked.append({
                "opportunity_id": opportunity.id,
                "title": opportunity.title,
                "description": opportunity.description or "",
                "category": opportunity.category.value if opportunity.category else "scholarship",
                "relevance_score": combined_relevance,
                "semantic_score": semantic_score,
                "query_specific_score": query_specific_score,
                "eligibility_score": eligibility["score"],
                "eligibility": eligibility,
                "deadline": opportunity.deadline.isoformat() if opportunity.deadline else None,
                "amount": opportunity.amount_max or opportunity.amount_min,
                "source_url": opportunity.application_url or opportunity.source_url,
            })
        
        # Sort by relevance and eligibility
        ranked.sort(key=lambda item: (item["relevance_score"], item["eligibility_score"]), reverse=True)
        
        # Apply relaxed threshold for better recall
        filtered_ranked = [item for item in ranked if item["relevance_score"] >= 0.3]  # Lowered from 0.5
        
        return filtered_ranked[:limit]
    
    def _calculate_query_specific_score_enhanced(self, query: str, opportunity: Opportunity) -> float:
        """Enhanced query-specific relevance scoring with comprehensive keyword analysis."""
        query_lower = query.lower()
        score = 0.0
        
        # Title relevance analysis (highest weight)
        title_lower = opportunity.title.lower()
        query_words = [word for word in query_lower.split() if len(word) > 3]
        title_matches = sum(1 for word in query_words if word in title_lower)
        if title_matches > 0:
            score += min(0.4, title_matches * 0.15)  # Up to 40% from title matches
        
        # Description keyword analysis
        if opportunity.description:
            desc_lower = opportunity.description.lower()
            desc_matches = sum(1 for word in query_words if word in desc_lower)
            if desc_matches > 0:
                score += min(0.3, desc_matches * 0.08)  # Up to 30% from description
        
        # Enhanced category-specific analysis
        category_boosters = {
            "engineering": {
                "keywords": ["engineering", "technical", "computer", "mechanical", "electrical", "civil", "electronics", "technology"],
                "boost": 0.15
            },
            "medical": {
                "keywords": ["medical", "medicine", "healthcare", "doctor", "nurse", "pharma", "biotechnology", "mbbs"],
                "boost": 0.15
            },
            "scholarship": {
                "keywords": ["scholarship", "financial", "aid", "grant", "stipend", "funding", "assistance"],
                "boost": 0.1
            },
            "research": {
                "keywords": ["research", "phd", "fellowship", "innovation", "inspire", "dst"],
                "boost": 0.1
            }
        }
        
        for category, config in category_boosters.items():
            if any(keyword in query_lower for keyword in config["keywords"]):
                if (opportunity.category and category in opportunity.category.value.lower()) or \
                   any(keyword in title_lower for keyword in config["keywords"]):
                    score += config["boost"]
        
        # Program-specific identifier matching
        program_identifiers = ["aicte", "ugc", "inspire", "nmms", "nsp", "mahadbt", "pragati", "saksham"]
        for identifier in program_identifiers:
            if identifier in query_lower and identifier in title_lower:
                score += 0.1
        
        return min(1.0, score)  # Cap at 1.0
    
    def _assess_content_completeness(self, opportunity: Opportunity) -> float:
        """Assess the completeness and quality of opportunity information."""
        completeness_score = 0.0
        
        # Essential information availability
        if opportunity.title:
            completeness_score += 0.2
        if opportunity.description and len(opportunity.description) > 50:
            completeness_score += 0.2
        if opportunity.amount_min or opportunity.amount_max:
            completeness_score += 0.2
        if opportunity.deadline:
            completeness_score += 0.2
        if opportunity.application_url or opportunity.source_url:
            completeness_score += 0.1
        if opportunity.eligibility_rules:
            completeness_score += 0.1
        
        return completeness_score
