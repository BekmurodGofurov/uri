import random

from fastapi import FastAPI

from shared.contracts import (
    Aspect,
    AspectHit,
    AspectResponse,
    AspectResult,
    ScoreRequest,
    Sentiment,
)

app = FastAPI(title="Aspect Service Stub")
MODEL_VERSION = "stub-aspect-v0.1.0"
ASPECTS: list[Aspect] = ["delivery", "quality", "price", "seller", "packaging", "other"]
POLARITIES: list[Sentiment] = ["negative", "neutral", "positive"]


@app.post("/v1/score", response_model=AspectResponse)
def score_aspects(request: ScoreRequest) -> AspectResponse:
    results: list[AspectResult] = []
    for review in request.reviews:
        # Sample 1 or 2 aspects
        chosen_aspects = random.sample(ASPECTS, k=random.randint(1, 2))
        hits = [
            AspectHit(
                aspect=asp,
                polarity=random.choice(POLARITIES),
                confidence=round(random.uniform(0.70, 0.98), 2),
            )
            for asp in chosen_aspects
        ]
        results.append(AspectResult(id=review.id, aspects=hits))
    return AspectResponse(results=results, model_version=MODEL_VERSION)


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": True}


@app.get("/model-info")
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "training_date": "2026-09-03",
        "headline_metric": "macro-f1: 0.80 (stub)",
    }
