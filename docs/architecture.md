# System Architecture

Uzum Review Intelligence (URI) is designed as a modular, decoupled microservices platform for processing, scoring, and visualizing Uzbek-language e-commerce product reviews.

---

## 1. System Overview

The platform ingests raw reviews, applies specialized text normalization for the Uzbek language, routes reviews concurrently to machine learning microservices, persists results to PostgreSQL, and serves aggregations to an interactive React dashboard.

```
                           +---------------------------+
                           |     Customer Reviews      |
                           +-------------+-------------+
                                         |
                                         v
+------------------+       +-------------+-------------+       +------------------+
|                  |       |                           |       |                  |
|  PostgreSQL 16   |<----->|      Gateway Service      |<----->| React Dashboard  |
|  (Persistence)   |       |        (Port 8000)        |       | (Port 5173/3000) |
+------------------+       +-------+-----------+-------+       +------------------+
                                   |           |
                     +-------------+           +-------------+
                     |                                       |
                     v                                       v
         +-----------+-----------+               +-----------+-----------+
         |     sentiment-svc     |               |      aspect-svc       |
         |      (Port 8001)      |               |      (Port 8002)      |
         +-----------------------+               +-----------------------+
```

---

## 2. Core Components

### 2.1 Gateway Service (`gateway/`)
- Host: FastAPI on Port 8000.
- Purpose: Central API orchestrator, data validation, database persistence, and model registry management.
- Responsibilities:
  - Ingests single reviews or batches via `POST /api/reviews/batch`.
  - Dispatches parallel HTTP requests to `sentiment-svc` and `aspect-svc`.
  - Persists products, reviews, and model predictions into PostgreSQL.
  - Manages active model versions and one-command rollback via `gateway/registry/`.

### 2.2 Sentiment Service (`sentiment-svc/`)
- Host: FastAPI on Port 8001.
- Purpose: Classifies review polarity into `positive`, `neutral`, or `negative`.
- Model: TF-IDF vectorizer (1-2 n-grams, 100k features) with balanced Logistic Regression.
- Endpoints:
  - `POST /v1/score`: Scores input text.
  - `GET /health`: Healthcheck endpoint.
  - `GET /model-info`: Active model metadata and version.

### 2.3 Aspect Service (`aspect-svc/`)
- Host: FastAPI on Port 8002.
- Purpose: Extracts fine-grained operational categories (`delivery`, `quality`, `price`, `seller`, `packaging`, `other`) and per-aspect polarities.
- Endpoints:
  - `POST /v1/aspects`: Extracts aspect tags and polarities.
  - `GET /health`: Healthcheck endpoint.
  - `GET /model-info`: Active model metadata.

### 2.4 Analytics Dashboard (`dashboard/`)
- Host: React 18, TypeScript, Tailwind CSS, Vite on Port 5173 (or 3000).
- Purpose: Visualizes product ratings, aspect breakdown matrices, sentiment distributions, and provides a real-time review scoring playground.

### 2.5 Relational Database (`postgres`)
- Image: PostgreSQL 16 Alpine.
- Tables:
  - `products`: Product catalog identifiers and metadata.
  - `reviews`: Raw and normalized review text with ratings.
  - `predictions`: Stored sentiment scores, confidence values, and aspect extractions.
  - `model_versions`: Historical record of deployed model versions for rollback.

---

## 3. Communication and Data Contracts

### 3.1 Contract Decoupling
Services maintain strict decoupling:
- Neither `sentiment-svc` nor `aspect-svc` imports gateway or database logic.
- Cross-service schemas are defined exclusively in `shared/contracts.py`.

### 3.2 Frozen Contract Definitions
The following core data models in `shared/contracts.py` govern all inter-service traffic:
- `Sentiment`: Enum representing `positive`, `neutral`, and `negative`.
- `Aspect`: Enum representing `delivery`, `quality`, `price`, `seller`, `packaging`, and `other`.
- `SentimentRequest`: Single-text payload sent to `sentiment-svc`.
- `SentimentResponse`: Prediction output containing predicted label, confidence score, and model version.
- `AspectRequest`: Single-text payload sent to `aspect-svc`.
- `AspectResponse`: Extraction output containing detected aspects with confidence and polarities.

---

## 4. Uzbek Text Normalization Pipeline

All text processing follows a deterministic normalization path (`preprocessing/normalizer.py`):
1. Script Consistency: Normalizes Cyrillic and Latin Uzbek text variations.
2. Apostrophe Harmonization: Standardizes all apostrophe variants (`'`, `ʻ`, `` ` ``, `ʼ`) to standard Unicode representations.
3. Whitespace and Character Cleaning: Strips control characters, normalizes repeated whitespace, and lowers casing where required by downstream vectorizers.
