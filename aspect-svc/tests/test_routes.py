import pytest
from app.main import app
from fastapi.testclient import TestClient

ALL_ASPECTS = {"delivery", "quality", "price", "seller", "packaging", "other"}
ALL_POLARITIES = {"negative", "neutral", "positive"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("MODEL_TYPE", "keyword_stub")
    monkeypatch.setenv("MODEL_VERSION", "aspect-test-v1")
    with TestClient(app) as c:
        yield c


def test_score_200(client):
    r = client.post(
        "/v1/score", json={"reviews": [{"id": "r1", "text": "Yetkazib berish tez edi."}]}
    )
    assert r.status_code == 200


def test_score_response_shape(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": "Sifat juda yaxshi."}]})
    data = r.json()
    assert "results" in data
    assert "model_version" in data

    result = data["results"][0]
    assert result["id"] == "r1"
    assert isinstance(result["aspects"], list)
    assert len(result["aspects"]) >= 1
    for hit in result["aspects"]:
        assert hit["aspect"] in ALL_ASPECTS
        assert hit["polarity"] in ALL_POLARITIES
        assert 0.0 <= hit["confidence"] <= 1.0


def test_multiple_reviews_scored_independently(client):
    r = client.post(
        "/v1/score",
        json={
            "reviews": [
                {"id": "r1", "text": "Narx juda arzon edi."},
                {"id": "r2", "text": "Qadoq yorilib ketgan edi."},
            ]
        },
    )
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 2
    assert {res["id"] for res in results} == {"r1", "r2"}


def test_review_can_have_multiple_aspects(client):
    text = "Yetkazib berish yomon edi, narx juda qimmat edi."
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": text}]})
    aspects = {hit["aspect"] for hit in r.json()["results"][0]["aspects"]}
    assert "delivery" in aspects
    assert "price" in aspects
    assert len(aspects) >= 2


def test_no_keyword_match_falls_back_to_other(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": "Bu oddiy sharh matni."}]})
    aspects = {hit["aspect"] for hit in r.json()["results"][0]["aspects"]}
    assert aspects == {"other"}


def test_empty_reviews_rejected(client):
    r = client.post("/v1/score", json={"reviews": []})
    assert r.status_code == 422


def test_missing_text_rejected(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1"}]})
    assert r.status_code == 422


def test_empty_text_rejected(client):
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": ""}]})
    assert r.status_code == 422


def test_text_over_max_length_rejected(client):
    long_text = "a" * 5001
    r = client.post("/v1/score", json={"reviews": [{"id": "r1", "text": long_text}]})
    assert r.status_code == 422


def test_batch_over_64_rejected(client):
    reviews = [{"id": str(i), "text": "matn"} for i in range(65)]
    r = client.post("/v1/score", json={"reviews": reviews})
    assert r.status_code == 422


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ["ok", "error"]
    assert body["model_loaded"] is True
    assert "model_version" in body


def test_model_info_lists_all_aspects(client):
    r = client.get("/model-info")
    assert r.status_code == 200
    data = r.json()
    assert "model_version" in data
    assert "macro_f1" in data
    assert set(data["aspects"]) == ALL_ASPECTS
