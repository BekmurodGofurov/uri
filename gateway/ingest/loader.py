import argparse
import logging
from typing import Any

from sqlalchemy.orm import Session

from gateway.database.connection import get_engine, init_db
from gateway.database.models import Product, Review

logger = logging.getLogger(__name__)


def ingest_reviews_batch(session: Session, items: list[dict[str, Any]]) -> int:
    """Ingest a list of review dictionaries into the database.

    Expected keys in item:
      - id: str
      - text: str
      - rating: int (optional, 1-5)
      - product_id: str (optional)
      - product_title: str (optional)
    """
    count = 0
    for item in items:
        review_id = str(item["id"])
        product_id = item.get("product_id")

        if product_id:
            product = session.get(Product, product_id)
            if not product:
                product = Product(
                    id=product_id,
                    title=item.get("product_title", f"Product {product_id}"),
                )
                session.add(product)
                session.flush()

        existing = session.get(Review, review_id)
        if not existing:
            review = Review(
                id=review_id,
                product_id=product_id,
                text=item["text"],
                rating=item.get("rating"),
            )
            session.add(review)
            count += 1

    session.commit()
    return count


RATING_MAP = {
    "very poor": 1,
    "poor": 2,
    "fair": 3,
    "good": 4,
    "excellent": 5,
}


def parse_rating(val: Any) -> int | None:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    str_val = str(val).strip().lower()
    if str_val in RATING_MAP:
        return RATING_MAP[str_val]
    try:
        num = int(str_val)
        if 1 <= num <= 5:
            return num
    except ValueError:
        pass
    return None


def load_from_huggingface(limit: int = 1000) -> None:
    """Load reviews directly from HuggingFace dataset."""
    from datasets import load_dataset

    from gateway.database.connection import get_session

    print(f"Loading dataset from HuggingFace (limit={limit})...")
    ds = load_dataset("risqaliyevds/uzbek-sentiment-analysis", split="train")

    init_db()
    with next(get_session()) as session:
        batch = []
        for idx, row in enumerate(ds):
            if idx >= limit:
                break
            batch.append(
                {
                    "id": f"hf_{idx}",
                    "text": row["normalized_review_text"],
                    "rating": parse_rating(row.get("rating")),
                    "product_id": f"prod_{(idx % 20) + 1}",
                }
            )
            if len(batch) >= 100:
                inserted = ingest_reviews_batch(session, batch)
                print(f"Ingested {inserted} reviews...")
                batch = []

        if batch:
            inserted = ingest_reviews_batch(session, batch)
            print(f"Ingested {inserted} reviews.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Uzum reviews into PostgreSQL")
    parser.add_argument("--limit", type=int, default=500, help="Maximum rows to load")
    args = parser.parse_args()

    init_db(get_engine())
    load_from_huggingface(limit=args.limit)
