from platform.database.connection import get_session
from platform.database.models import Prediction, Product, Review
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

app = FastAPI(title="Uzum Review Intelligence Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    yield from get_session()


class SentimentSummary(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ProductListItem(BaseModel):
    id: str
    title: str | None
    category: str | None
    review_count: int
    avg_rating: float | None
    sentiment_summary: SentimentSummary


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "gateway"}


@app.get("/api/products", response_model=list[ProductListItem])
def list_products(db: Annotated[Session, Depends(get_db)]) -> list[ProductListItem]:
    products = list(db.scalars(select(Product).order_by(Product.id)).all())

    items: list[ProductListItem] = []
    for prod in products:
        # Reviews stats
        rev_count = (
            db.scalar(select(func.count(Review.id)).where(Review.product_id == prod.id)) or 0
        )
        avg_rat = db.scalar(select(func.avg(Review.rating)).where(Review.product_id == prod.id))
        rounded_avg = round(float(avg_rat), 2) if avg_rat is not None else None

        # Sentiment counts
        sent_counts = dict(
            db.execute(
                select(Prediction.sentiment_label, func.count(Prediction.id))
                .join(Review, Prediction.review_id == Review.id)
                .where(Review.product_id == prod.id)
                .group_by(Prediction.sentiment_label)
            ).all()
        )

        summary = SentimentSummary(
            positive=sent_counts.get("positive", 0),
            neutral=sent_counts.get("neutral", 0),
            negative=sent_counts.get("negative", 0),
        )

        items.append(
            ProductListItem(
                id=prod.id,
                title=prod.title,
                category=prod.category,
                review_count=rev_count,
                avg_rating=rounded_avg,
                sentiment_summary=summary,
            )
        )

    return items
