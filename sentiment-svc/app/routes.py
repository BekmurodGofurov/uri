from fastapi import APIRouter, HTTPException

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
        raise HTTPException(status_code=500, detail=str(e))

    results = [
        PredictionResult(id=id_, label=p["label"], confidence=p["confidence"])
        for id_, p in zip(ids, predictions)
    ]
    return ScoreResponse(results=results, model_version=get_version())


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        get_model()
        loaded = True
    except RuntimeError:
        loaded = False
    return HealthResponse(
        status="ok" if loaded else "error",
        model_loaded=loaded,
        model_version=get_version(),
    )


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model_version=get_version(),
        model_type=get_type(),
        training_data="2026-09-04",
        heading_metrics="macro-f2: 0.6241",
    )
