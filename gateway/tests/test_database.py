from gateway.database.connection import get_database_url, get_session, init_db
from gateway.database.models import Prediction, Product, Review

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


def test_database_url_resolution(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    default_url = get_database_url()
    assert "sqlite" in default_url

    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/db")
    pg_url = get_database_url()
    assert "postgresql+psycopg://" in pg_url


def test_product_and_review_creation(db_session: Session):
    product = Product(id="prod_1", title="Wireless Earbuds", category="Electronics")
    db_session.add(product)
    db_session.commit()

    review = Review(
        id="rev_1",
        product_id="prod_1",
        text="Ajoyib ovoz sifati!",
        rating=5,
    )
    db_session.add(review)
    db_session.commit()

    # Query back
    saved_prod = db_session.get(Product, "prod_1")
    assert saved_prod is not None
    assert len(saved_prod.reviews) == 1
    assert saved_prod.reviews[0].text == "Ajoyib ovoz sifati!"


def test_prediction_creation_and_cascade_delete(db_session: Session):
    review = Review(id="rev_2", text="Yaxshi mahsulot", rating=4)
    db_session.add(review)
    db_session.commit()

    prediction = Prediction(
        review_id="rev_2",
        sentiment_label="positive",
        sentiment_confidence=0.92,
        aspects=[{"aspect": "quality", "polarity": "positive", "confidence": 0.9}],
        model_version="v1.0.0-test",
    )
    db_session.add(prediction)
    db_session.commit()

    stmt = select(Prediction).where(Prediction.review_id == "rev_2")
    preds = list(db_session.scalars(stmt).all())
    assert len(preds) == 1
    assert preds[0].model_version == "v1.0.0-test"
    assert preds[0].sentiment_label == "positive"
    assert len(preds[0].aspects) == 1

    # Cascade delete
    db_session.delete(review)
    db_session.commit()

    deleted_preds = list(
        db_session.scalars(select(Prediction).where(Prediction.review_id == "rev_2")).all()
    )
    assert len(deleted_preds) == 0


def test_get_session():
    generator = get_session("sqlite:///:memory:")
    session = next(generator)
    assert isinstance(session, Session)
    # Trigger generator cleanup
    with pytest.raises(StopIteration):
        next(generator)
