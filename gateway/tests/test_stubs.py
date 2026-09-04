from gateway.stubs.aspect_stub import app as aspect_app
from gateway.stubs.sentiment_stub import app as sentiment_app

from fastapi.testclient import TestClient

from shared.contracts import AspectResponse, ScoreRequest, SentimentResponse


def test_sentiment_stub_health_and_info():
    client = TestClient(sentiment_app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["model_loaded"] is True

    info = client.get("/model-info")
    assert info.status_code == 200
    data = info.json()
    assert "model_version" in data
    assert data["model_version"].startswith("stub-sentiment")


def test_sentiment_stub_scoring():
    client = TestClient(sentiment_app)
    req = ScoreRequest(
        reviews=[
            {"id": "rev_1", "text": "Juda yaxshi tovar!"},
            {"id": "rev_2", "text": "Umuman yoqmadi, rasvo."},
        ]
    )
    res = client.post("/v1/score", json=req.model_dump())
    assert res.status_code == 200
    parsed = SentimentResponse.model_validate(res.json())
    assert len(parsed.results) == 2
    assert parsed.results[0].id == "rev_1"
    assert parsed.results[0].label in ["positive", "neutral", "negative"]
    assert 0.0 <= parsed.results[0].confidence <= 1.0
    assert parsed.model_version == "stub-sentiment-v0.1.0"


def test_aspect_stub_health_and_info():
    client = TestClient(aspect_app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    info = client.get("/model-info")
    assert info.status_code == 200
    assert "model_version" in info.json()


def test_aspect_stub_scoring():
    client = TestClient(aspect_app)
    req = ScoreRequest(
        reviews=[
            {"id": "rev_10", "text": "Dostavka kechikdi lekin kiyim sifati a'lo"},
        ]
    )
    res = client.post("/v1/score", json=req.model_dump())
    assert res.status_code == 200
    parsed = AspectResponse.model_validate(res.json())
    assert len(parsed.results) == 1
    assert parsed.results[0].id == "rev_10"
    assert len(parsed.results[0].aspects) >= 1
    assert parsed.results[0].aspects[0].aspect in [
        "delivery",
        "quality",
        "price",
        "seller",
        "packaging",
        "other",
    ]
