from pydantic import BaseModel, Field
from typing import Literal

class ReviewItem(BaseModel):
    id: str = Field(..., description="Unique review ID")
    text: str = Field(..., min_length=1, max_length=5000)


class ScoreRequest(BaseModel):
    reviews: list[ReviewItem] = Field(..., min_length=1, max_length=64)


class PredictionResult(BaseModel):
    id: str
    label: Literal["positive", "neutral", "negative"]
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


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
    training_data: str = '2026-09-04'
    heading_metrics: str = 'macro-f2: 0.6241'
    num_classes: int = 3
    labels: list[str] = ["negative", "neutral", "positive"]