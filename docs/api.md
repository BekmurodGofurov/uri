# API Reference

This document provides complete endpoint specifications for the Gateway Service and upstream machine learning services.

---

## 1. Gateway API (Port 8000)

Base URL: `http://localhost:8000`

### 1.1 System Health
`GET /api/health`
- Description: Verifies gateway status, database connection, and downstream service connectivity.
- Response (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "sentiment": "healthy",
    "aspect": "healthy"
  }
}
```

### 1.2 Ingest and Score Batch
`POST /api/reviews/batch`
- Description: Ingests, normalizes, scores sentiment and aspects, and stores reviews in PostgreSQL.
- Headers: `X-API-Key: <your-key>` (if authentication is enabled)
- Request Body:
```json
{
  "product_id": "prod_123",
  "reviews": [
    {
      "review_id": "rev_001",
      "text": "Yetkazib berish juda tez bo'ldi, mahsulot sifati a'lo darajada.",
      "rating": 5
    }
  ]
}
```
- Response (200 OK):
```json
{
  "processed": 1,
  "successful": 1,
  "failed": 0
}
```

### 1.3 Ad-Hoc Scoring Playground
`POST /api/score`
- Description: Scores review text for sentiment and aspects without persisting records to the database.
- Request Body:
```json
{
  "text": "Narxi qimmat ekan, lekin sifati yaxshi."
}
```
- Response (200 OK):
```json
{
  "sentiment": {
    "label": "neutral",
    "score": 0.74,
    "model_version": "sentiment-v1"
  },
  "aspects": [
    {
      "aspect": "price",
      "polarity": "negative",
      "confidence": 0.88
    },
    {
      "aspect": "quality",
      "polarity": "positive",
      "confidence": 0.82
    }
  ]
}
```

### 1.4 Product Analytics Endpoints
- `GET /api/products`: Lists products with aggregated review counts and sentiment breakdown.
- `GET /api/products/{product_id}/sentiment`: Detailed sentiment statistics (positive, neutral, negative counts and percentages).
- `GET /api/products/{product_id}/aspects`: Aggregated aspect mentions and aspect-level polarity breakdown.
- `GET /api/products/{product_id}/reviews`: Paginated drill-down of reviews filtered by sentiment or aspect tag.

---

## 2. Sentiment Service API (Port 8001)

Base URL: `http://localhost:8001`

### 2.1 Score Sentiment
`POST /v1/score`
- Request Body:
```json
{
  "text": "Mahsulot juda sifatli."
}
```
- Response (200 OK):
```json
{
  "label": "positive",
  "score": 0.941,
  "model_version": "sentiment-v1"
}
```

### 2.2 Service Health
`GET /health`
- Response: `{"status": "ok"}`

### 2.3 Model Information
`GET /model-info`
- Response:
```json
{
  "version": "sentiment-v1",
  "algorithm": "TF-IDF + LogisticRegression",
  "macro_f1": 0.6241
}
```

---

## 3. Aspect Service API (Port 8002)

Base URL: `http://localhost:8002`

### 3.1 Extract Aspects
`POST /v1/aspects`
- Request Body:
```json
{
  "text": "Karobkasi yirtilgan holda yetib keldi."
}
```
- Response (200 OK):
```json
{
  "aspects": [
    {
      "aspect": "packaging",
      "polarity": "negative",
      "confidence": 0.89
    },
    {
      "aspect": "delivery",
      "polarity": "neutral",
      "confidence": 0.71
    }
  ],
  "model_version": "aspect-multilabel-v1"
}
```

### 3.2 Service Health and Metadata
- `GET /health`: Healthcheck endpoint.
- `GET /model-info`: Active model metadata and supported aspect categories.
