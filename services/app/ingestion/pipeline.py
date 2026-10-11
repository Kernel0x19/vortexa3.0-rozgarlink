"""Ingestion pipeline orchestrator."""

from typing import Dict, Any
from sqlalchemy.orm import Session
import asyncio

from app.ingestion.connector_registry import ConnectorOrchestrator


def run_ingestion(db: Session) -> Dict[str, Any]:
    """Run ingestion for all enabled opportunity and hackathon connectors."""
    orchestrator = ConnectorOrchestrator(
        db,
        config={"enabled_connectors": ["unstop", "devfolio", "mlh", "unstop_internships", "internshala", "aicte"]},
    )
    # Run async orchestrator in loop
    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(orchestrator.run_all())
    finally:
        loop.close()

    total_processed = sum(r.get("processed", 0) for r in results)
    return {
        "status": "success",
        "connectors_run": len(results),
        "total_records_processed": total_processed,
        "results": results,
    }
