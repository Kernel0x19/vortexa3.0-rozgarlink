"""Dynamic Connector Registry and Orchestrator.

Manages connector registrations, manual and scheduled triggers, status tracking,
and data freshness metrics.
"""

from typing import Dict, Any, List, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.models import ConnectorStatus
from app.ingestion.base import BaseConnector
from app.ingestion.connectors import (
    UnstopHackathonsConnector,
    DevfolioHackathonsConnector,
    MLHHackathonsConnector,
    UnstopInternshipsConnector,
    InternshalaConnector,
    AICTEInternshipConnector,
)

logger = logging.getLogger(__name__)

CONNECTOR_MAP: Dict[str, Type[BaseConnector]] = {
    "unstop": UnstopHackathonsConnector,
    "devfolio": DevfolioHackathonsConnector,
    "mlh": MLHHackathonsConnector,
    "hackathons": UnstopHackathonsConnector,
    "unstop_internships": UnstopInternshipsConnector,
    "internshala": InternshalaConnector,
    "aicte": AICTEInternshipConnector,
    "internships": InternshalaConnector,
}


class ConnectorOrchestrator:
    """Manages connector executions and status tracking."""

    def __init__(self, db: Session, config: Optional[Dict[str, Any]] = None):
        self.db = db
        self.config = config or {}

    def get_registered_connectors(self) -> List[str]:
        """Return list of registered connector names."""
        return list(CONNECTOR_MAP.keys())

    async def run_connector(self, connector_name: str) -> Dict[str, Any]:
        """Run a single named connector and record execution metrics."""
        name_lower = connector_name.lower().strip()
        connector_cls = CONNECTOR_MAP.get(name_lower)

        status_rec = self.db.query(ConnectorStatus).filter_by(name=name_lower).first()
        if not status_rec:
            status_rec = ConnectorStatus(name=name_lower)
            self.db.add(status_rec)

        status_rec.last_run = datetime.utcnow()

        if not connector_cls:
            status_rec.last_error = f"Unknown connector: {connector_name}"
            status_rec.is_stale = True
            self.db.commit()
            return {
                "connector": connector_name,
                "status": "error",
                "error": f"Unknown connector: {connector_name}",
                "processed": 0,
            }

        try:
            connector_instance = connector_cls(self.db, self.config)
            result = await connector_instance.run()

            if result.get("status") == "success":
                status_rec.last_success = datetime.utcnow()
                status_rec.records_processed = status_rec.records_processed + result.get("processed", 0)
                status_rec.is_stale = False
                status_rec.last_error = None
            else:
                status_rec.last_error = result.get("error")

            self.db.commit()
            return result
        except Exception as exc:
            self.db.rollback()
            status_rec.last_error = str(exc)
            status_rec.is_stale = True
            self.db.commit()
            return {
                "connector": connector_name,
                "status": "error",
                "error": str(exc),
                "processed": 0,
            }

    async def run_all(self) -> List[Dict[str, Any]]:
        """Run all configured connectors."""
        connectors = self.config.get(
            "enabled_connectors",
            ["unstop", "devfolio", "mlh", "internshala", "aicte"],
        )
        results = []
        for name in connectors:
            res = await self.run_connector(name)
            results.append(res)
        return results
