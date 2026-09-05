from app.schemas import HealthResponse, ModelInfoResponse
from fastapi import APIRouter, HTTPException
from models.model_loader import get_aspects, get_macro_f1, get_model, get_type, get_version
from training.inference import predict

from shared.contracts import AspectResponse, AspectResult, ScoreRequest

router = APIRouter()


@router.post("/v1/score", response_model=AspectResponse)
def score(request: ScoreRequest) -> AspectResponse:
    ids = [r.id for r in request.reviews]
    texts = [r.text for r in request.reviews]

    try:
        predictions = predict(texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    results = [
        AspectResult(id=id_, aspects=hits) for id_, hits in zip(ids, predictions, strict=True)
    ]
    return AspectResponse(results=results, model_version=get_version())


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
        trained_on="n/a (rule-based stub)",
        macro_f1=get_macro_f1(),
        aspects=get_aspects(),
    )
