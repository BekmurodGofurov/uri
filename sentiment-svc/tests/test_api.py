import os
import sys
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

_sentiment_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _sentiment_dir not in sys.path:
    sys.path.insert(0, _sentiment_dir)

from app import model_loader  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("MODEL_TYPE", "tfidf")
    monkeypatch.setenv("MODEL_VERSION", "sentiment-test-v1")
    monkeypatch.setenv("MODEL_PATH", "models/tfidf_v1.joblib")

    mock = MagicMock()
    mock.predict_proba.side_effect = lambda texts: [[0.05, 0.10, 0.85]] * len(texts)

    monkeypatch.setattr(model_loader, "_model", mock)
    yield TestClient(app)


def test_score_200(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": "Yaxshi mahsulot"}]})
    assert r.status_code == 200


def test_score_fields(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": "Yaxshi"}]})
    data = r.json()
    assert "results" in data
    assert "model_version" in data
    res = data["results"][0]
    assert res["id"] == "r1"
    assert res["label"] in ["positive", "neutral", "negative"]
    assert 0.0 <= res["confidence"] <= 1.0


def test_empty_reviews_rejected(client):
    r = client.post("/v1/score", json={"reviews": []})
    assert r.status_code == 422


def test_missing_text_rejected(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1"}]})
    assert r.status_code == 422


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ["ok", "error"]


def test_model_info(client):
    r = client.get("/model-info")
    assert r.status_code == 200
    data = r.json()
    assert "model_version" in data
    assert "model_type" in data


def test_multiple_reviews(client):
    r = client.post(
        "/v1/score",
        json={
            "reviews": [
                {"id": "r1", "text": "Yaxshi"},
                {"id": "r2", "text": "Yomon"},
            ]
        },
    )
    assert r.status_code == 200
    assert len(r.json()["results"]) == 2
