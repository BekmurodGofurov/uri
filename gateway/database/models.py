from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    product_id: Mapped[str | None] = mapped_column(
        String(128), ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    product: Mapped[Product | None] = relationship("Product", back_populates="reviews")
    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction", back_populates="review", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("rating IS NULL OR (rating BETWEEN 1 AND 5)", name="ck_reviews_rating"),
        Index("idx_reviews_product_id", "product_id"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    sentiment_label: Mapped[str] = mapped_column(String(32), nullable=False)
    sentiment_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    aspects: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    model_version: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), nullable=False)

    review: Mapped[Review] = relationship("Review", back_populates="predictions")

    __table_args__ = (
        Index("idx_predictions_review_id", "review_id"),
        Index("idx_predictions_model_version", "model_version"),
    )
