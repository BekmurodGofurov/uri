from fastapi import APIRouter, HTTPException, status

from app.inference import predict
from app.model_loader import get_model, get_type, get_version
from app.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionResult,
    ScoreRequest,
    ScoreResponse,
)

router = APIRouter()


@router.post("/v1/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    texts = [r.text for r in request.reviews]  # <--- make sure 'texts' is defined here
    ids = [r.id for r in request.reviews]

    try:
        predictions = predict(texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    results = [
        PredictionResult(id=id_, label=p["label"], confidence=p["confidence"])
        for id_, p in zip(ids, predictions, strict=False)
    ]
    return ScoreResponse(results=results, model_version=get_version())


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        get_model()
        loaded = True
    except RuntimeError:
        loaded = False
    content = HealthResponse(
        status="ok" if loaded else "error",
        model_loaded=loaded,
        model_version=get_version(),
    )
    if not loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded",
        )
    return content


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model_version=get_version(),
        model_type=get_type(),
        training_date="2026-09-04",
        headline_metric="macro-f1: 0.6241",
    )
