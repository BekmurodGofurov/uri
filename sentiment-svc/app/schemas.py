"""App schemas — imports strictly from shared.contracts.

The shared package is available because:
  - In Docker: PYTHONPATH=/workspace is set in the Dockerfile, which adds the
    monorepo root so `shared/` is importable.
  - In local dev: run from the repo root, or set PYTHONPATH=. manually.

There is NO try/except fallback here. If shared.contracts is unavailable the
service should fail fast with an ImportError rather than silently running with
locally-redefined types that may drift from the frozen contract.
"""

from typing import Literal

from pydantic import BaseModel

from shared.contracts import ReviewIn as ReviewItem  # noqa: F401 (re-exported)
from shared.contracts import (
    ScoreRequest,  # noqa: F401 (re-exported)
    Sentiment,  # noqa: F401 (re-exported)
)
from shared.contracts import SentimentResponse as ScoreResponse  # noqa: F401 (re-exported)
from shared.contracts import SentimentResult as PredictionResult  # noqa: F401 (re-exported)


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
