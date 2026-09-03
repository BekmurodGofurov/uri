from platform.api.app import app, get_db
from platform.database.models import Base, Prediction, Product, Review

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


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
