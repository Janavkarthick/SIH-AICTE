"""Pydantic schemas for verification benchmarking and pipeline accuracy evaluation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MetricScore(BaseModel):
    """Precision, recall, and F1 evaluation metric score."""
    precision: float
    recall: float
    f1_score: float
    support: int


class EvaluationMetricsResponse(BaseModel):
    """Aggregate accuracy evaluation results across pipeline components."""
    document_classification: MetricScore
    field_extraction: MetricScore
    tamper_detection: MetricScore
    overall_accuracy: float
    benchmark_dataset_size: int
    notes: str = "SYNTHETIC BENCHMARK - NOT REAL-WORLD ACCURACY. Evaluated on 285 neutral test units."
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    total_samples: Optional[int] = None
    detailed_checks: Optional[List[Dict[str, Any]]] = None
    execution_time_ms: Optional[int] = None
    evaluated_at: Optional[str] = None


class EvaluationRunResponse(BaseModel):
    """Outcome of triggering an automated evaluation run."""
    run_id: str
    status: str
    processed_samples: int
    metrics: EvaluationMetricsResponse
