from typing import Literal

from pydantic import BaseModel, Field

# Attempt import from shared.contracts; fallback to local definition for standalone docker
try:
    from shared.contracts import (
        ReviewIn as ReviewItem,
    )
    from shared.contracts import (
        ScoreRequest,
        Sentiment,
    )
    from shared.contracts import (
        SentimentResponse as ScoreResponse,
    )
    from shared.contracts import (
        SentimentResult as PredictionResult,
    )
except ImportError:
    Sentiment = Literal["negative", "neutral", "positive"]

    class ReviewItem(BaseModel):
        id: str = Field(..., description="Unique review ID")
        text: str = Field(..., min_length=1, max_length=5000)

    class ScoreRequest(BaseModel):
        reviews: list[ReviewItem] = Field(..., min_length=1, max_length=64)

    class PredictionResult(BaseModel):
        id: str
        label: Sentiment
        confidence: float = Field(..., ge=0.0, le=1.0)

    class ScoreResponse(BaseModel):
        results: list[PredictionResult]
        model_version: str


class HealthResponse(BaseModel):
    status: Literal["ok", "error"]
    model_loaded: bool
    model_version: str


class ModelInfoResponse(BaseModel):
    model_version: str
    model_type: str
    training_date: str = "2026-09-04"
    headline_metric: str = "macro-f1: 0.6241"
    num_classes: int = 3
    labels: list[str] = ["negative", "neutral", "positive"]
