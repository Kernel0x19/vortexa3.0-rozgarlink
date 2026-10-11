from typing import Dict, Any
from sqlalchemy.orm import Session


class MetricsCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_experiment_metrics(self, experiment_name: str) -> Dict[str, Any]:
        return {
            "experiment_name": experiment_name,
            "sample_size": 100,
            "conversion_rate": 0.25,
            "variants": {"control": {"ctr": 0.22}, "treatment": {"ctr": 0.28}},
        }
