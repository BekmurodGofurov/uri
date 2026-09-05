import logging
import os
import uuid
from collections.abc import Generator
from typing import Annotated, Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gateway.database.connection import get_session
from gateway.database.models import Prediction, Product, Review
from gateway.ingest.pipeline import score_and_store_batch, score_only_batch
from shared.contracts import Sentiment

logger = logging.getLogger(__name__)

# API key for protecting write endpoints (read from .env / environment)
API_KEY: str | None = os.getenv("API_KEY")

app = FastAPI(title="Uzum Review Intelligence Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_db():
    yield from get_session()


def get_ml_clients() -> Generator[tuple[httpx.Client, httpx.Client], None, None]:
    with httpx.Client(timeout=10.0) as sent_c, httpx.Client(timeout=10.0) as asp_c:
        yield sent_c, asp_c


DEFAULT_PRODUCT_ID = "prod_1"


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
    if not products:
        return []

    # 1 query for all review counts and averages, grouped by product (resolves N+1)
    stats = db.execute(
        select(Review.product_id, func.count(Review.id), func.avg(Review.rating))
        .where(Review.product_id.is_not(None))
        .group_by(Review.product_id)
    ).all()
    stats_map = {pid: (cnt, avg) for pid, cnt, avg in stats}

    # 1 query for all sentiment counts, grouped by product and label
    sentiment_rows = db.execute(
        select(Review.product_id, Prediction.sentiment_label, func.count(Prediction.id))
        .join(Prediction, Prediction.review_id == Review.id)
        .where(Review.product_id.is_not(None))
        .group_by(Review.product_id, Prediction.sentiment_label)
    ).all()
    sent_map: dict[str, dict[str, int]] = {}
    for pid, label, count in sentiment_rows:
        if pid not in sent_map:
            sent_map[pid] = {}
        sent_map[pid][label] = count

    items: list[ProductListItem] = []
    for prod in products:
        rev_count, avg_rat = stats_map.get(prod.id, (0, None))
        rounded_avg = round(float(avg_rat), 2) if avg_rat is not None else None
        prod_sent = sent_map.get(prod.id, {})

        summary = SentimentSummary(
            positive=prod_sent.get("positive", 0),
            neutral=prod_sent.get("neutral", 0),
            negative=prod_sent.get("negative", 0),
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

    # Aggregate stats directly in DB (avoids unbounded memory usage)
    rev_stats = db.execute(
        select(func.count(Review.id), func.avg(Review.rating)).where(
            Review.product_id == product_id
        )
    ).first()
    rev_count = rev_stats[0] if rev_stats else 0
    avg_rat = round(float(rev_stats[1]), 2) if rev_stats and rev_stats[1] is not None else None

    # Load only lightweight prediction and timestamp data — no Review.text!
    pred_rows = db.execute(
        select(
            Review.created_at,
            Prediction.sentiment_label,
            Prediction.aspects,
            Prediction.model_version,
        )
        .join(Review, Prediction.review_id == Review.id)
        .where(Review.product_id == product_id)
        .order_by(Review.created_at)
    ).all()

    # Sentiment over time & summary
    sent_counts = {"positive": 0, "neutral": 0, "negative": 0}
    time_points: dict[str, dict[str, int]] = {}
    aspect_tallies: dict[str, dict[str, int]] = {}
    model_versions: set[str] = set()

    for rev_created_at, sentiment_label, aspects, model_version in pred_rows:
        if sentiment_label in sent_counts:
            sent_counts[sentiment_label] += 1

        dt = (
            rev_created_at.strftime("%Y-%m-%d")
            if hasattr(rev_created_at, "strftime")
            else str(rev_created_at)[:10]
        )
        if dt not in time_points:
            time_points[dt] = {"positive": 0, "neutral": 0, "negative": 0}
        if sentiment_label in time_points[dt]:
            time_points[dt][sentiment_label] += 1

        if isinstance(aspects, list):
            for hit in aspects:
                asp = hit.get("aspect")
                pol = hit.get("polarity", "neutral")
                if asp:
                    if asp not in aspect_tallies:
                        aspect_tallies[asp] = {"positive": 0, "neutral": 0, "negative": 0}
                    if pol in aspect_tallies[asp]:
                        aspect_tallies[asp][pol] += 1

        if model_version:
            model_versions.add(model_version)

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


class ReviewPredictionItem(BaseModel):
    id: int
    sentiment_label: Sentiment
    sentiment_confidence: float
    aspects: list[dict[str, Any]]
    model_version: str
    created_at: str


class ProductReviewItem(BaseModel):
    id: str
    text: str
    rating: int | None
    created_at: str
    prediction: ReviewPredictionItem | None


class ProductReviewsResponse(BaseModel):
    product_id: str
    total: int
    limit: int
    offset: int
    reviews: list[ProductReviewItem]


@app.get("/api/products/{product_id}/reviews", response_model=ProductReviewsResponse)
def get_product_reviews(
    product_id: str,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    sentiment: Annotated[Sentiment | None, Query()] = None,
) -> ProductReviewsResponse:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")

    stmt = select(Review).where(Review.product_id == product_id)
    if sentiment:
        stmt = stmt.join(Prediction, Review.id == Prediction.review_id).where(
            Prediction.sentiment_label == sentiment
        )

    total_count = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Review.created_at.desc(), Review.id.desc()).offset(offset).limit(limit)
    reviews = list(db.scalars(stmt).all())

    rev_ids = [r.id for r in reviews]
    pred_stmt = select(Prediction).where(Prediction.review_id.in_(rev_ids))
    preds = list(db.scalars(pred_stmt).all()) if rev_ids else []
    pred_map = {p.review_id: p for p in preds}

    items: list[ProductReviewItem] = []
    for r in reviews:
        pred = pred_map.get(r.id)
        pred_item = None
        if pred:
            pred_item = ReviewPredictionItem(
                id=pred.id,
                sentiment_label=pred.sentiment_label,  # type: ignore
                sentiment_confidence=pred.sentiment_confidence,
                aspects=pred.aspects or [],
                model_version=pred.model_version,
                created_at=pred.created_at.isoformat(),
            )

        items.append(
            ProductReviewItem(
                id=r.id,
                text=r.text,
                rating=r.rating,
                created_at=r.created_at.isoformat(),
                prediction=pred_item,
            )
        )

    return ProductReviewsResponse(
        product_id=product_id,
        total=total_count,
        limit=limit,
        offset=offset,
        reviews=items,
    )


class ScoreItemRequest(BaseModel):
    id: str | None = None  # Optional — server generates if missing
    text: str = Field(min_length=1, max_length=5000)
    rating: int | None = Field(default=None, ge=1, le=5)
    product_id: str | None = DEFAULT_PRODUCT_ID


class GatewayScoreRequest(BaseModel):
    reviews: list[ScoreItemRequest] = Field(min_length=1, max_length=64)


class ScoreItemResult(BaseModel):
    id: int
    review_id: str
    sentiment_label: Sentiment
    sentiment_confidence: float
    aspects: list[dict[str, Any]]
    model_version: str


class GatewayScoreResponse(BaseModel):
    scored_count: int
    predictions: list[ScoreItemResult]


# ── Preview result (no DB id, lighter schema) ────────────────────────────────


class PreviewItemResult(BaseModel):
    review_id: str
    text: str
    sentiment_label: Sentiment
    sentiment_confidence: float
    aspects: list[dict[str, Any]]
    model_version: str


class PreviewScoreResponse(BaseModel):
    scored_count: int
    predictions: list[PreviewItemResult]


# ── /api/score/preview — demo endpoint, saves NOTHING to DB ──────────────────


@app.post("/api/score/preview", response_model=PreviewScoreResponse)
def preview_score(
    req: GatewayScoreRequest,
    ml_clients: Annotated[tuple[httpx.Client, httpx.Client], Depends(get_ml_clients)],
) -> PreviewScoreResponse:
    """Score review text and return results. Nothing is saved to the database.

    This is the endpoint the dashboard Live Scorer uses so that demo
    sentences do not pollute the production reviews table.
    """
    sent_client, asp_client = ml_clients

    review_dicts = [
        {"id": item.id or f"preview_{uuid.uuid4().hex[:12]}", "text": item.text}
        for item in req.reviews
    ]

    try:
        results = score_only_batch(
            reviews=review_dicts,
            sentiment_client=sent_client,
            aspect_client=asp_client,
        )
    except Exception:
        logger.exception("Preview scoring failed for %d reviews", len(req.reviews))
        raise HTTPException(status_code=502, detail="Scoring service unavailable") from None

    return PreviewScoreResponse(
        scored_count=len(results),
        predictions=[PreviewItemResult(**r) for r in results],
    )


# ── API key dependency ────────────────────────────────────────────────────────


def _verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    """Reject the request unless the caller provides a valid API key.

    When ``API_KEY`` is not configured (e.g. local dev), the check is skipped
    so existing workflows are not broken.
    """
    if API_KEY is None:
        return  # no key configured — allow (dev mode)
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


# ── /api/score — protected, writes to DB ─────────────────────────────────────


@app.post("/api/score", response_model=GatewayScoreResponse)
def score_reviews_endpoint(
    req: GatewayScoreRequest,
    db: Annotated[Session, Depends(get_db)],
    ml_clients: Annotated[tuple[httpx.Client, httpx.Client], Depends(get_ml_clients)],
    _key: Annotated[None, Depends(_verify_api_key)] = None,
) -> GatewayScoreResponse:
    sent_client, asp_client = ml_clients

    reviews_to_score: list[Review] = []

    for item in req.reviews:
        # Server generates the review ID — never trust the client
        review_id = item.id or f"rev_{uuid.uuid4().hex}"

        # Reject if a review with this ID already exists (no silent overwrite)
        existing = db.get(Review, review_id)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Review '{review_id}' already exists. Use a unique ID.",
            )

        prod_id = item.product_id or DEFAULT_PRODUCT_ID
        prod = db.get(Product, prod_id)
        if not prod:
            prod = Product(id=prod_id, title=f"Product {prod_id}")
            db.add(prod)
            db.flush()

        review = Review(
            id=review_id,
            text=item.text,
            rating=item.rating,
            product_id=prod_id,
        )
        db.add(review)
        db.flush()
        reviews_to_score.append(review)

    try:
        saved_preds = score_and_store_batch(
            session=db,
            reviews=reviews_to_score,
            sentiment_client=sent_client,
            aspect_client=asp_client,
        )
    except Exception:
        logger.exception("Scoring failed for batch of %d reviews", len(reviews_to_score))
        db.rollback()
        raise HTTPException(status_code=502, detail="Scoring service unavailable") from None

    results = [
        ScoreItemResult(
            id=p.id,
            review_id=p.review_id,
            sentiment_label=p.sentiment_label,  # type: ignore
            sentiment_confidence=p.sentiment_confidence,
            aspects=p.aspects or [],
            model_version=p.model_version,
        )
        for p in saved_preds
    ]

    return GatewayScoreResponse(
        scored_count=len(results),
        predictions=results,
    )
