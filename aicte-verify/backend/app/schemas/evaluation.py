"""Pydantic schemas for verification benchmarking and pipeline accuracy evaluation."""

from typing import Any, Dict, List
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
    notes: str = "SIMULATED benchmark evaluation against synthetic annotated ground truth"


class EvaluationRunResponse(BaseModel):
    """Outcome of triggering an automated evaluation run."""
    run_id: str
    status: str
    processed_samples: int
    metrics: EvaluationMetricsResponse
