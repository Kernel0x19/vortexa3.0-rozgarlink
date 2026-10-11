from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class VariantCreate(BaseModel):
    variant_name: str
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ExperimentCreate(BaseModel):
    experiment_name: str
    variants: List[VariantCreate]


class ExperimentVariantResponse(BaseModel):
    id: str
    experiment_name: str
    variant_name: str
    is_active: bool
    config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ExperimentComparisonResponse(BaseModel):
    experiment_name: str
    metrics: Dict[str, Any]


class ExperimentMetricsResponse(BaseModel):
    experiment_name: str
    metrics: Dict[str, Any]


class ExperimentSummary(BaseModel):
    experiment_name: str
    variants_count: int


class PromoteVariantRequest(BaseModel):
    variant_name: str


class PromoteVariantResponse(BaseModel):
    experiment_name: str
    promoted_variant: str
    success: bool


class UserAssignmentResponse(BaseModel):
    user_id: str
    experiment_name: str
    variant_name: str
