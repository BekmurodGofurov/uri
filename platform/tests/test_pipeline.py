from platform.database.models import Base, Prediction, Product, Review
from platform.ingest.loader import ingest_reviews_batch
from platform.ingest.pipeline import process_unscored_reviews, score_and_store_batch
from platform.stubs.aspect_stub import app as aspect_app
from platform.stubs.sentiment_stub import app as sentiment_app

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


def test_ingest_reviews_batch(db_session: Session):
    items = [
        {
            "id": "rev_101",
            "text": "Zo'r mahsulot!",
            "rating": 5,
            "product_id": "prod_1",
            "product_title": "Quloqchin",
        },
        {
            "id": "rev_102",
            "text": "Sifatsiz narsa",
            "rating": 1,
            "product_id": "prod_1",
        },
    ]
    inserted = ingest_reviews_batch(db_session, items)
    assert inserted == 2

    # Check product created
    prod = db_session.get(Product, "prod_1")
    assert prod is not None
    assert prod.title == "Quloqchin"

    # Check reviews created
    reviews = list(db_session.scalars(select(Review)).all())
    assert len(reviews) == 2


def test_pipeline_score_and_store(db_session: Session):
    # Ingest 2 reviews
    items = [
        {"id": "r1", "text": "Kiyim juda chiroyli", "rating": 5},
        {"id": "r2", "text": "Kechikib keldi", "rating": 2},
    ]
    ingest_reviews_batch(db_session, items)

    reviews = list(db_session.scalars(select(Review)).all())

    # Create TestClients for both stubs
    from fastapi.testclient import TestClient

    sent_client = TestClient(sentiment_app)
    asp_client = TestClient(aspect_app)

    preds = score_and_store_batch(
        session=db_session,
        reviews=reviews,
        sentiment_client=sent_client,  # type: ignore
        aspect_client=asp_client,  # type: ignore
        sentiment_url="http://testserver",
        aspect_url="http://testserver",
    )

    assert len(preds) == 2
    assert preds[0].sentiment_label in ["positive", "neutral", "negative"]
    assert "stub-sentiment" in preds[0].model_version
    assert "stub-aspect" in preds[0].model_version
    assert isinstance(preds[0].aspects, list)

    # Verify persisted in database
    db_preds = list(db_session.scalars(select(Prediction)).all())
    assert len(db_preds) == 2


def test_process_unscored_reviews(db_session: Session):
    items = [{"id": "r_unscored", "text": "Yaxshi mahsulot", "rating": 4}]
    ingest_reviews_batch(db_session, items)

    from fastapi.testclient import TestClient

    sent_client = TestClient(sentiment_app)
    asp_client = TestClient(aspect_app)

    processed = process_unscored_reviews(
        session=db_session,
        sentiment_client=sent_client,  # type: ignore
        aspect_client=asp_client,  # type: ignore
    )
    assert processed == 1

    # Second run should find 0 unscored reviews
    processed_again = process_unscored_reviews(
        session=db_session,
        sentiment_client=sent_client,  # type: ignore
        aspect_client=asp_client,  # type: ignore
    )
    assert processed_again == 0
