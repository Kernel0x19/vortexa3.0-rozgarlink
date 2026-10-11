from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import ExperimentVariant, UserExperiment


class ExperimentService:
    def __init__(self, db: Session):
        self.db = db

    def create_experiment(self, experiment_name: str, variants: List[Dict[str, Any]]) -> List[ExperimentVariant]:
        created = []
        for v in variants:
            ev = ExperimentVariant(
                experiment_name=experiment_name,
                variant_name=v.get("variant_name", "control"),
                is_active=v.get("is_active", True),
                config=v.get("config", {}),
            )
            self.db.add(ev)
            created.append(ev)
        self.db.commit()
        return created

    def get_user_variant(self, user_id: str, experiment_name: str) -> str:
        assignment = self.db.query(UserExperiment).filter_by(user_id=user_id, experiment_name=experiment_name).first()
        if assignment:
            return assignment.variant_name

        variants = self.db.query(ExperimentVariant).filter_by(experiment_name=experiment_name, is_active=True).all()
        if not variants:
            return "control"

        chosen = variants[hash(user_id) % len(variants)].variant_name
        assignment = UserExperiment(
            user_id=user_id,
            experiment_name=experiment_name,
            variant_name=chosen,
            assigned_at=datetime.utcnow(),
        )
        self.db.add(assignment)
        self.db.commit()
        return chosen

    def get_all_experiments(self) -> List[str]:
        rows = self.db.query(ExperimentVariant.experiment_name).distinct().all()
        return [r[0] for r in rows]

    def get_variants(self, experiment_name: str) -> List[ExperimentVariant]:
        return self.db.query(ExperimentVariant).filter_by(experiment_name=experiment_name).all()
