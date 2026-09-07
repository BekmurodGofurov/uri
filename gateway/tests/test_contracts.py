import pytest
from pydantic import ValidationError

from shared.contracts import (
    AspectHit,
    AspectResponse,
    AspectResult,
    ReviewIn,
    ScoreRequest,
    SentimentResponse,
    SentimentResult,
)


def test_review_in_valid():
    rev = ReviewIn(id="rev_1", text="Juda a'lo sifatli mahsulot!")
    assert rev.id == "rev_1"
    assert rev.text == "Juda a'lo sifatli mahsulot!"


def test_review_in_empty_text_rejected():
    with pytest.raises(ValidationError):
        ReviewIn(id="rev_2", text="")


def test_score_request_batch_limit():
    # Empty batch should be rejected
    with pytest.raises(ValidationError):
        ScoreRequest(reviews=[])

    # Valid batch within limits (1 to 64)
    reviews = [ReviewIn(id=f"r_{i}", text=f"Review text {i}") for i in range(10)]
    req = ScoreRequest(reviews=reviews)
    assert len(req.reviews) == 10

    # Batch > 64 should be rejected
    too_many = [ReviewIn(id=f"r_{i}", text=f"Review text {i}") for i in range(65)]
    with pytest.raises(ValidationError):
        ScoreRequest(reviews=too_many)


def test_sentiment_response_valid():
    res = SentimentResult(id="rev_1", label="positive", confidence=0.95)
    resp = SentimentResponse(results=[res], model_version="v1.0.0-test")
    assert resp.model_version == "v1.0.0-test"
    assert resp.results[0].label == "positive"
    assert resp.results[0].confidence == 0.95


def test_invalid_sentiment_label_rejected():
    with pytest.raises(ValidationError):
        SentimentResult(id="rev_1", label="unknown_label", confidence=0.5)  # type: ignore


def test_aspect_response_valid():
    hit = AspectHit(aspect="delivery", polarity="negative", confidence=0.88)
    aspect_res = AspectResult(id="rev_1", aspects=[hit])
    resp = AspectResponse(results=[aspect_res], model_version="v1.0.0-aspect-test")
    assert resp.model_version == "v1.0.0-aspect-test"
    assert len(resp.results[0].aspects) == 1
    assert resp.results[0].aspects[0].aspect == "delivery"


def test_invalid_aspect_rejected():
    with pytest.raises(ValidationError):
        AspectHit(aspect="non_existing_aspect", polarity="positive", confidence=0.9)  # type: ignore
