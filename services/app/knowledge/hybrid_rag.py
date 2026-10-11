import hashlib
import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.config import get_settings
from app.db.models import Opportunity, StudentProfile
from app.intelligence.eligibility import evaluate_eligibility

logger = logging.getLogger(__name__)
settings = get_settings()

VECTOR_DIM = 384  # all-MiniLM-L6-v2 output dimension


class HybridRAG:
    """Structured DB (SQLAlchemy) + FAISS vector store for semantic search."""

    INDEX_FILE = "faiss_index.bin"
    META_FILE = "faiss_meta.pkl"

    def __init__(self) -> None:
        self._store_path = Path(settings.chroma_path)
        self._store_path.mkdir(parents=True, exist_ok=True)

        self._index_path = self._store_path / self.INDEX_FILE
        self._meta_path = self._store_path / self.META_FILE

        # id_map: faiss internal int → metadata dict
        # embedding_id_to_faiss: embedding_id str → faiss internal int
        self._id_map: dict[int, dict] = {}
        self._embedding_id_to_faiss: dict[str, int] = {}
        self._next_id: int = 0

        self._index: faiss.IndexFlatIP | None = None
        self._load_or_create_index()

        # Lazy-loaded embedding model
        self._embedder = None

    # ------------------------------------------------------------------
    # Index persistence
    # ------------------------------------------------------------------

    def _load_or_create_index(self) -> None:
        if self._index_path.exists() and self._meta_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            with open(self._meta_path, "rb") as f:
                state = pickle.load(f)
            self._id_map = state["id_map"]
            self._embedding_id_to_faiss = state["embedding_id_to_faiss"]
            self._next_id = state["next_id"]
        else:
            # IndexFlatIP with normalised vectors == cosine similarity
            self._index = faiss.IndexFlatIP(VECTOR_DIM)

    def _save_index(self) -> None:
        faiss.write_index(self._index, str(self._index_path))
        with open(self._meta_path, "wb") as f:
            pickle.dump(
                {
                    "id_map": self._id_map,
                    "embedding_id_to_faiss": self._embedding_id_to_faiss,
                    "next_id": self._next_id,
                },
                f,
            )

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self._embedder

    def _embed(self, text: str) -> np.ndarray:
        vec = self._get_embedder().encode(text, normalize_embeddings=True)
        return vec.astype(np.float32).reshape(1, -1)

    # ------------------------------------------------------------------
    # Document text
    # ------------------------------------------------------------------

    def _doc_text(self, opp: Opportunity) -> str:
        parts = [opp.title, opp.description or ""]

        if opp.amount_min or opp.amount_max:
            lo = f"\u20b9{opp.amount_min:,}" if opp.amount_min else ""
            hi = f"\u20b9{opp.amount_max:,}" if opp.amount_max else ""
            if lo and hi:
                parts.append(f"Amount: {lo}\u2013{hi} per annum")
            elif hi:
                parts.append(f"Amount: up to {hi} per annum")
            elif lo:
                parts.append(f"Amount: {lo} per annum")

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

        if opp.documents_required:
            parts.append(f"Documents required: {', '.join(opp.documents_required)}")
        if opp.tags:
            parts.append(" ".join(opp.tags))

        return " ".join(parts)

    def _embedding_str_id(self, opp: Opportunity) -> str:
        return hashlib.sha256(f"{opp.source}:{opp.external_id}".encode()).hexdigest()[:32]

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index_opportunity(self, opp: Opportunity) -> str:
        doc_id = self._embedding_str_id(opp)
        text = self._doc_text(opp)
        vector = self._embed(text)

        if doc_id in self._embedding_id_to_faiss:
            # Overwrite not supported in IndexFlatIP — mark old slot as deleted
            # by leaving it in place (scores won't surface if metadata is gone)
            old_faiss_id = self._embedding_id_to_faiss[doc_id]
            del self._id_map[old_faiss_id]

        faiss_id = self._next_id
        self._next_id += 1

        self._index.add_with_ids(vector, np.array([faiss_id], dtype=np.int64))
        self._id_map[faiss_id] = {
            "embedding_id": doc_id,
            "opportunity_id": opp.id,
            "source": opp.source,
            "category": opp.category.value if opp.category else "scholarship",
            "title": opp.title[:200],
        }
        self._embedding_id_to_faiss[doc_id] = faiss_id

        opp.embedding_id = doc_id
        self._save_index()
        return doc_id

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def semantic_search(
        self, query: str, limit: int = 20, category: str | None = None
    ) -> list[dict[str, Any]]:
        if self._index.ntotal == 0:
            return []

        processed_query = self._enhance_query_advanced(query)
        vector = self._embed(processed_query)
        search_limit = min(limit * 2, 40, self._index.ntotal)

        scores, faiss_ids = self._index.search(vector, search_limit)

        items = []
        for score, fid in zip(scores[0], faiss_ids[0]):
            if fid == -1:
                continue
            meta = self._id_map.get(int(fid))
            if meta is None:
                continue
            if category and meta.get("category") != category:
                continue
            if score < 0.2:
                continue
            items.append({
                "embedding_id": meta["embedding_id"],
                "opportunity_id": meta["opportunity_id"],
                "score": float(score),
                "title": meta["title"],
            })

        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:limit]

    # ------------------------------------------------------------------
    # Query enhancement
    # ------------------------------------------------------------------

    def _enhance_query_advanced(self, query: str) -> str:
        enhanced_query = query.lower()

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

        for keyword, enhancement in query_enhancements.items():
            if keyword in enhanced_query:
                enhanced_query += " " + enhancement

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

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def reindex_all(self, db) -> int:
        count = 0
        for opp in db.query(Opportunity).filter_by(is_active=True).all():
            self.index_opportunity(opp)
            count += 1
        db.commit()
        return count

    def retrieve_for_profile(
        self,
        db,
        query: str,
        profile: StudentProfile | None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        candidates = self.semantic_search(query, limit=max(limit * 3, 20), category="scholarship")
        ids = [item["opportunity_id"] for item in candidates if item.get("opportunity_id")]
        opportunities = {
            opp.id: opp
            for opp in db.query(Opportunity).filter(
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

        ranked.sort(
            key=lambda item: (item["relevance_score"], item["eligibility_score"]), reverse=True
        )
        filtered_ranked = [item for item in ranked if item["relevance_score"] >= 0.3]
        return filtered_ranked[:limit]

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _calculate_query_specific_score_enhanced(
        self, query: str, opportunity: Opportunity
    ) -> float:
        query_lower = query.lower()
        score = 0.0

        title_lower = opportunity.title.lower()
        query_words = [word for word in query_lower.split() if len(word) > 3]
        title_matches = sum(1 for word in query_words if word in title_lower)
        if title_matches > 0:
            score += min(0.4, title_matches * 0.15)

        if opportunity.description:
            desc_lower = opportunity.description.lower()
            desc_matches = sum(1 for word in query_words if word in desc_lower)
            if desc_matches > 0:
                score += min(0.3, desc_matches * 0.08)

        category_boosters = {
            "engineering": {
                "keywords": ["engineering", "technical", "computer", "mechanical", "electrical", "civil", "electronics", "technology"],
                "boost": 0.15,
            },
            "medical": {
                "keywords": ["medical", "medicine", "healthcare", "doctor", "nurse", "pharma", "biotechnology", "mbbs"],
                "boost": 0.15,
            },
            "scholarship": {
                "keywords": ["scholarship", "financial", "aid", "grant", "stipend", "funding", "assistance"],
                "boost": 0.1,
            },
            "research": {
                "keywords": ["research", "phd", "fellowship", "innovation", "inspire", "dst"],
                "boost": 0.1,
            },
        }

        for category, config in category_boosters.items():
            if any(keyword in query_lower for keyword in config["keywords"]):
                if (opportunity.category and category in opportunity.category.value.lower()) or \
                   any(keyword in title_lower for keyword in config["keywords"]):
                    score += config["boost"]

        program_identifiers = ["aicte", "ugc", "inspire", "nmms", "nsp", "mahadbt", "pragati", "saksham"]
        for identifier in program_identifiers:
            if identifier in query_lower and identifier in title_lower:
                score += 0.1

        return min(1.0, score)

    def _assess_content_completeness(self, opportunity: Opportunity) -> float:
        completeness_score = 0.0
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