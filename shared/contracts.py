"""Shared data contracts and Pydantic models for Uzum Review Intelligence (URI).

These contracts are frozen on Day 1. Any changes require unanimous agreement.
"""

from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["negative", "neutral", "positive"]
Aspect = Literal["delivery", "quality", "price", "seller", "packaging", "other"]


class ReviewIn(BaseModel):
    id: str
    text: str = Field(min_length=1, max_length=5000)


class ScoreRequest(BaseModel):
    reviews: list[ReviewIn] = Field(min_length=1, max_length=64)


class SentimentResult(BaseModel):
    id: str
    label: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)


class SentimentResponse(BaseModel):
    results: list[SentimentResult]
    model_version: str


class AspectHit(BaseModel):
    aspect: Aspect
    polarity: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)


class AspectResult(BaseModel):
    id: str
    aspects: list[AspectHit]


class AspectResponse(BaseModel):
    results: list[AspectResult]
    model_version: str
