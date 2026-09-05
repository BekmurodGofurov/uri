import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from gateway.api.app import app, get_db, get_ml_clients
from gateway.database.models import Base, Prediction, Product, Review
from gateway.stubs.aspect_stub import app as asp_app
from gateway.stubs.sentiment_stub import app as sent_app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    yield test_client, session_local()

    app.dependency_overrides.clear()


def test_health_check(client):
    test_client, _ = client
    res = test_client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "gateway"}


def test_list_products_empty(client):
    test_client, _ = client
    res = test_client.get("/api/products")
    assert res.status_code == 200
    assert res.json() == []


def test_list_products_with_data(client):
    test_client, db = client

    # Seed data
    prod = Product(id="prod_1", title="Himoya oynasi 9D", category="Aksessuarlar")
    db.add(prod)
    db.commit()

    rev1 = Review(id="r1", product_id="prod_1", text="Zo'r mahsulot!", rating=5)
    rev2 = Review(id="r2", product_id="prod_1", text="Sifatsiz ekan", rating=1)
    db.add_all([rev1, rev2])
    db.commit()

    pred1 = Prediction(
        review_id="r1",
        sentiment_label="positive",
        sentiment_confidence=0.95,
        aspects=[],
        model_version="v1",
    )
    pred2 = Prediction(
        review_id="r2",
        sentiment_label="negative",
        sentiment_confidence=0.88,
        aspects=[],
        model_version="v1",
    )
    db.add_all([pred1, pred2])
    db.commit()

    res = test_client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    p = data[0]
    assert p["id"] == "prod_1"
    assert p["title"] == "Himoya oynasi 9D"
    assert p["category"] == "Aksessuarlar"
    assert p["review_count"] == 2
    assert p["avg_rating"] == 3.0
    assert p["sentiment_summary"]["positive"] == 1
    assert p["sentiment_summary"]["negative"] == 1
    assert p["sentiment_summary"]["neutral"] == 0


def test_get_product_detail_not_found(client):
    test_client, _ = client
    res = test_client.get("/api/products/non_existing_prod")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_get_product_detail_success(client):
    test_client, db = client

    prod = Product(id="prod_phone", title="Smartfon X", category="Telefonlar")
    db.add(prod)
    db.commit()

    rev1 = Review(id="rev_p1", product_id="prod_phone", text="Sifati juda yaxshi", rating=5)
    rev2 = Review(id="rev_p2", product_id="prod_phone", text="Yetkazib berish kechikdi", rating=2)
    db.add_all([rev1, rev2])
    db.commit()

    pred1 = Prediction(
        review_id="rev_p1",
        sentiment_label="positive",
        sentiment_confidence=0.95,
        aspects=[{"aspect": "quality", "polarity": "positive", "confidence": 0.92}],
        model_version="stub-model-v1",
    )
    pred2 = Prediction(
        review_id="rev_p2",
        sentiment_label="negative",
        sentiment_confidence=0.89,
        aspects=[{"aspect": "delivery", "polarity": "negative", "confidence": 0.85}],
        model_version="stub-model-v1",
    )
    db.add_all([pred1, pred2])
    db.commit()

    res = test_client.get("/api/products/prod_phone")
    assert res.status_code == 200
    data = res.json()

    assert data["id"] == "prod_phone"
    assert data["title"] == "Smartfon X"
    assert data["review_count"] == 2
    assert data["avg_rating"] == 3.5
    assert data["sentiment_summary"]["positive"] == 1
    assert data["sentiment_summary"]["negative"] == 1
    assert data["sentiment_summary"]["neutral"] == 0

    assert len(data["sentiment_over_time"]) >= 1
    assert "stub-model-v1" in data["active_model_versions"]

    # Verify aspect breakdown
    aspect_dict = {a["aspect"]: a for a in data["aspect_breakdown"]}
    assert "quality" in aspect_dict
    assert aspect_dict["quality"]["positive"] == 1
    assert "delivery" in aspect_dict
    assert aspect_dict["delivery"]["negative"] == 1


def test_get_product_reviews_not_found(client):
    test_client, _ = client
    res = test_client.get("/api/products/non_existing/reviews")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_get_product_reviews_empty(client):
    test_client, db = client
    prod = Product(id="prod_empty", title="Bo'sh tovar")
    db.add(prod)
    db.commit()

    res = test_client.get("/api/products/prod_empty/reviews")
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == "prod_empty"
    assert data["total"] == 0
    assert data["reviews"] == []


def test_get_product_reviews_with_predictions_and_filter(client):
    test_client, db = client

    prod = Product(id="prod_shoes", title="Krossovka")
    db.add(prod)
    db.commit()

    rev1 = Review(id="rev_sh1", product_id="prod_shoes", text="Zo'r oyoq kiyim!", rating=5)
    rev2 = Review(id="rev_sh2", product_id="prod_shoes", text="Kichik keldi, siqdi", rating=2)
    rev3 = Review(id="rev_sh3", product_id="prod_shoes", text="Hali kiyib ko'rmadim", rating=3)
    db.add_all([rev1, rev2, rev3])
    db.commit()

    pred1 = Prediction(
        review_id="rev_sh1",
        sentiment_label="positive",
        sentiment_confidence=0.96,
        aspects=[{"aspect": "quality", "polarity": "positive", "confidence": 0.9}],
        model_version="stub-v1",
    )
    pred2 = Prediction(
        review_id="rev_sh2",
        sentiment_label="negative",
        sentiment_confidence=0.88,
        aspects=[{"aspect": "quality", "polarity": "negative", "confidence": 0.85}],
        model_version="stub-v1",
    )
    # rev_sh3 has NO prediction yet
    db.add_all([pred1, pred2])
    db.commit()

    # 1. Fetch all reviews
    res = test_client.get("/api/products/prod_shoes/reviews")
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == "prod_shoes"
    assert data["total"] == 3
    assert len(data["reviews"]) == 3

    # Check that predictions are populated
    rev_map = {r["id"]: r for r in data["reviews"]}
    assert rev_map["rev_sh1"]["prediction"] is not None
    assert rev_map["rev_sh1"]["prediction"]["sentiment_label"] == "positive"
    assert rev_map["rev_sh2"]["prediction"] is not None
    assert rev_map["rev_sh2"]["prediction"]["sentiment_label"] == "negative"
    assert rev_map["rev_sh3"]["prediction"] is None

    # 2. Filter by sentiment=positive
    res_pos = test_client.get("/api/products/prod_shoes/reviews?sentiment=positive")
    assert res_pos.status_code == 200
    data_pos = res_pos.json()
    assert data_pos["total"] == 1
    assert data_pos["reviews"][0]["id"] == "rev_sh1"

    # 3. Pagination: limit=1, offset=1
    res_page = test_client.get("/api/products/prod_shoes/reviews?limit=1&offset=1")
    assert res_page.status_code == 200
    data_page = res_page.json()
    assert data_page["total"] == 3
    assert len(data_page["reviews"]) == 1
    assert data_page["limit"] == 1
    assert data_page["offset"] == 1


def test_post_score_empty_rejected(client):
    test_client, _ = client
    res = test_client.post("/api/score", json={"reviews": []})
    assert res.status_code == 422


def test_post_score_success(client):
    test_client, db = client
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)

    payload = {
        "reviews": [
            {
                "id": "new_rev_1",
                "text": "Juda zo'r xarid bo'ldi, tavsiya qilaman!",
                "rating": 5,
                "product_id": "prod_phone_1",
            },
            {
                "id": "new_rev_2",
                "text": "Yetkazib berish juda sekin, buzilib keldi.",
                "rating": 1,
                "product_id": "prod_phone_1",
            },
        ]
    }

    res = test_client.post("/api/score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scored_count"] == 2
    assert len(data["predictions"]) == 2

    prod = db.get(Product, "prod_phone_1")
    assert prod is not None

    rev1 = db.get(Review, "new_rev_1")
    assert rev1 is not None
    assert rev1.rating == 5

    preds = list(
        db.query(Prediction).filter(Prediction.review_id.in_(["new_rev_1", "new_rev_2"])).all()
    )
    assert len(preds) == 2


def test_post_score_duplicate_id_rejected(client):
    """Sending a review with an ID that already exists must return 409."""
    test_client, db = client
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)

    # Insert a review directly
    db.add(Review(id="dup_1", text="Existing review", rating=4))
    db.commit()

    payload = {"reviews": [{"id": "dup_1", "text": "Trying to overwrite"}]}
    res = test_client.post("/api/score", json=payload)
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]


def test_post_score_generates_id_when_missing(client):
    """When the client omits 'id', the server should generate one."""
    test_client, _ = client
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)

    payload = {"reviews": [{"text": "No ID provided here"}]}
    res = test_client.post("/api/score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scored_count"] == 1
    # Server-generated ID should start with "rev_"
    assert data["predictions"][0]["review_id"].startswith("rev_")


def test_post_score_ml_failure(client):
    test_client, _ = client

    class FailingClient:
        def post(self, *args, **kwargs):
            raise RuntimeError("ML service unreachable")

    app.dependency_overrides[get_ml_clients] = lambda: (FailingClient(), FailingClient())

    payload = {"reviews": [{"id": "fail_1", "text": "Testing failure"}]}
    res = test_client.post("/api/score", json=payload)
    assert res.status_code == 502
    # Error message should be generic — no internal details leaked
    assert res.json()["detail"] == "Scoring service unavailable"


def test_post_score_rejected_without_api_key(client, monkeypatch):
    """When API_KEY is configured, requests without the header are rejected."""
    import sys

    app_module = sys.modules["gateway.api.app"]
    monkeypatch.setattr(app_module, "API_KEY", "test-secret-key")

    test_client, _ = client
    payload = {"reviews": [{"text": "Should be rejected"}]}
    res = test_client.post("/api/score", json=payload)
    assert res.status_code == 403

    # With the correct key it should pass
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)
    res2 = test_client.post(
        "/api/score",
        json=payload,
        headers={"X-API-Key": "test-secret-key"},
    )
    assert res2.status_code == 200


# ── Preview endpoint tests ───────────────────────────────────────────────────


def test_preview_score_success(client):
    """Preview endpoint returns results without saving to DB."""
    test_client, db = client
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)

    payload = {"reviews": [{"text": "Demo tahlil — bazaga yozilmasin"}]}
    res = test_client.post("/api/score/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scored_count"] == 1
    pred = data["predictions"][0]
    assert pred["sentiment_label"] in ["positive", "neutral", "negative"]
    assert pred["text"] == "Demo tahlil — bazaga yozilmasin"

    # Verify nothing was saved to the database
    from sqlalchemy import select as sa_select

    reviews = list(db.execute(sa_select(Review)).scalars().all())
    preds = list(db.execute(sa_select(Prediction)).scalars().all())
    assert len(reviews) == 0
    assert len(preds) == 0


def test_preview_does_not_require_api_key(client, monkeypatch):
    """Preview endpoint should work even when API_KEY is configured."""
    import sys

    app_module = sys.modules["gateway.api.app"]
    monkeypatch.setattr(app_module, "API_KEY", "test-secret-key")

    test_client, _ = client
    sent_c = TestClient(sent_app)
    asp_c = TestClient(asp_app)
    app.dependency_overrides[get_ml_clients] = lambda: (sent_c, asp_c)

    payload = {"reviews": [{"text": "Preview should always work"}]}
    res = test_client.post("/api/score/preview", json=payload)
    assert res.status_code == 200
