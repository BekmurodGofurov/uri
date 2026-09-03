from platform.database.connection import get_session
from platform.database.models import Prediction, Product, Review
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
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


class AspectPolaritySummary(BaseModel):
    aspect: str
    positive: int = 0
    neutral: int = 0
    negative: int = 0
    total: int = 0


class SentimentTimePoint(BaseModel):
    date: str
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ProductDetailResponse(BaseModel):
    id: str
    title: str | None
    category: str | None
    review_count: int
    avg_rating: float | None
    sentiment_summary: SentimentSummary
    sentiment_over_time: list[SentimentTimePoint]
    aspect_breakdown: list[AspectPolaritySummary]
    active_model_versions: list[str]


@app.get("/api/products/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> ProductDetailResponse:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")

    reviews = list(
        db.scalars(
            select(Review).where(Review.product_id == product_id).order_by(Review.created_at)
        ).all()
    )
    rev_count = len(reviews)
    ratings_list = [r.rating for r in reviews if r.rating is not None]
    avg_rat = round(sum(ratings_list) / len(ratings_list), 2) if ratings_list else None

    # Get predictions for these reviews
    review_ids = [r.id for r in reviews]
    predictions = (
        list(db.scalars(select(Prediction).where(Prediction.review_id.in_(review_ids))).all())
        if review_ids
        else []
    )

    # Review created_at lookup for time grouping
    review_date_map = {r.id: r.created_at.strftime("%Y-%m-%d") for r in reviews}

    # Sentiment over time & summary
    sent_counts = {"positive": 0, "neutral": 0, "negative": 0}
    time_points: dict[str, dict[str, int]] = {}
    aspect_tallies: dict[str, dict[str, int]] = {}
    model_versions: set[str] = set()

    for pred in predictions:
        if pred.sentiment_label in sent_counts:
            sent_counts[pred.sentiment_label] += 1

        dt = review_date_map.get(pred.review_id, "unknown")
        if dt not in time_points:
            time_points[dt] = {"positive": 0, "neutral": 0, "negative": 0}
        if pred.sentiment_label in time_points[dt]:
            time_points[dt][pred.sentiment_label] += 1

        if isinstance(pred.aspects, list):
            for hit in pred.aspects:
                asp = hit.get("aspect")
                pol = hit.get("polarity", "neutral")
                if asp:
                    if asp not in aspect_tallies:
                        aspect_tallies[asp] = {"positive": 0, "neutral": 0, "negative": 0}
                    if pol in aspect_tallies[asp]:
                        aspect_tallies[asp][pol] += 1

        if pred.model_version:
            model_versions.add(pred.model_version)

    sentiment_over_time = [
        SentimentTimePoint(date=d, **counts) for d, counts in sorted(time_points.items())
    ]

    aspect_breakdown = [
        AspectPolaritySummary(
            aspect=asp,
            positive=counts["positive"],
            neutral=counts["neutral"],
            negative=counts["negative"],
            total=sum(counts.values()),
        )
        for asp, counts in sorted(aspect_tallies.items())
    ]

    return ProductDetailResponse(
        id=product.id,
        title=product.title,
        category=product.category,
        review_count=rev_count,
        avg_rating=avg_rat,
        sentiment_summary=SentimentSummary(**sent_counts),
        sentiment_over_time=sentiment_over_time,
        aspect_breakdown=aspect_breakdown,
        active_model_versions=sorted(model_versions),
    )
