import random

from fastapi import FastAPI

from shared.contracts import ScoreRequest, Sentiment, SentimentResponse, SentimentResult

app = FastAPI(title="Sentiment Service Stub")
MODEL_VERSION = "stub-sentiment-v0.1.0"
LABELS: list[Sentiment] = ["negative", "neutral", "positive"]


@app.post("/v1/score", response_model=SentimentResponse)
def score_reviews(request: ScoreRequest) -> SentimentResponse:
    results: list[SentimentResult] = []
    for review in request.reviews:
        # Simple deterministic or pseudo-random label for stability in tests
        label = random.choice(LABELS)
        confidence = round(random.uniform(0.75, 0.99), 2)
        results.append(SentimentResult(id=review.id, label=label, confidence=confidence))
    return SentimentResponse(results=results, model_version=MODEL_VERSION)


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": True}


@app.get("/model-info")
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "training_date": "2026-09-03",
        "headline_metric": "macro-f1: 0.85 (stub)",
    }
