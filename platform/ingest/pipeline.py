import logging
import os
from platform.database.models import Prediction, Review
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.contracts import AspectResponse, ReviewIn, ScoreRequest, SentimentResponse

logger = logging.getLogger(__name__)

DEFAULT_SENTIMENT_SVC_URL = os.getenv("SENTIMENT_SVC_URL", "http://localhost:8001")
DEFAULT_ASPECT_SVC_URL = os.getenv("ASPECT_SVC_URL", "http://localhost:8002")


def score_and_store_batch(
    session: Session,
    reviews: list[Review],
    sentiment_client: httpx.Client,
    aspect_client: httpx.Client,
    sentiment_url: str = DEFAULT_SENTIMENT_SVC_URL,
    aspect_url: str = DEFAULT_ASPECT_SVC_URL,
) -> list[Prediction]:
    """Score a batch of reviews against both ML services and store predictions in DB."""
    if not reviews:
        return []

    # Prepare ScoreRequest
    items = [ReviewIn(id=r.id, text=r.text) for r in reviews]
    request = ScoreRequest(reviews=items)
    req_dict = request.model_dump()

    # Call sentiment service
    sent_res = sentiment_client.post(f"{sentiment_url.rstrip('/')}/v1/score", json=req_dict)
    sent_res.raise_for_status()
    sentiment_resp = SentimentResponse.model_validate(sent_res.json())

    # Call aspect service
    asp_res = aspect_client.post(f"{aspect_url.rstrip('/')}/v1/score", json=req_dict)
    asp_res.raise_for_status()
    aspect_resp = AspectResponse.model_validate(asp_res.json())

    # Map responses by ID
    sent_map = {res.id: res for res in sentiment_resp.results}
    aspect_map = {res.id: [h.model_dump() for h in res.aspects] for res in aspect_resp.results}

    # Combined model version
    combined_model_version = f"{sentiment_resp.model_version};{aspect_resp.model_version}"

    saved_predictions: list[Prediction] = []
    for review in reviews:
        sent_item = sent_map.get(review.id)
        if not sent_item:
            continue

        aspect_hits: list[dict[str, Any]] = aspect_map.get(review.id, [])

        prediction = Prediction(
            review_id=review.id,
            sentiment_label=sent_item.label,
            sentiment_confidence=sent_item.confidence,
            aspects=aspect_hits,
            model_version=combined_model_version,
        )
        session.add(prediction)
        saved_predictions.append(prediction)

    session.commit()
    return saved_predictions


def process_unscored_reviews(
    session: Session,
    sentiment_client: httpx.Client,
    aspect_client: httpx.Client,
    batch_size: int = 32,
) -> int:
    """Find reviews without predictions and process them in batches."""
    stmt = (
        select(Review)
        .outerjoin(Prediction, Review.id == Prediction.review_id)
        .where(Prediction.id.is_(None))
        .limit(batch_size)
    )
    unscored = list(session.scalars(stmt).all())
    if not unscored:
        return 0

    saved = score_and_store_batch(session, unscored, sentiment_client, aspect_client)
    return len(saved)
