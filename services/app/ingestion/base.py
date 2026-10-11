"""Base connector interface for data ingestion.

All connectors for hackathons, internships, and platform schemes inherit from BaseConnector.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session


class BaseConnector(ABC):
    """Abstract base class for all RozgarLink data connectors."""

    name: str = "base"
    category: str = "general"

    def __init__(self, db: Session, config: Dict[str, Any] | None = None):
        self.db = db
        self.config = config or {}

    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw records from the data source (API, scraper, or feed)."""
        pass

    @abstractmethod
    def normalize_and_store(self, raw_records: List[Dict[str, Any]]) -> int:
        """Normalize raw items, deduplicate, and upsert to database.
        
        Returns the count of successfully processed records.
        """
        pass

    async def run(self) -> Dict[str, Any]:
        """Execute full fetch + normalize cycle."""
        try:
            records = await self.fetch()
            processed = self.normalize_and_store(records)
            return {
                "connector": self.name,
                "status": "success",
                "fetched": len(records),
                "processed": processed,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "connector": self.name,
                "status": "error",
                "error": str(e),
                "processed": 0,
                "timestamp": datetime.utcnow().isoformat(),
            }
