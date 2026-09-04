# Uzum Review Intelligence (URI) 🛍️📊

An end-to-end Machine Learning and analytics platform designed to analyze Uzbek-language e-commerce product reviews. URI automatically performs sentiment analysis, extracts fine-grained aspect polarities (delivery, quality, price, seller, packaging), provides a real-time interactive analytical dashboard, and features a versioned model registry with one-command rollback capabilities.

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)
![Tests](https://img.shields.io/badge/Tests-Passing%20(48%2F48)-success)

---

## 📌 Table of Contents

- [1. Project Overview & Problem Statement](#1-project-overview--problem-statement)
- [2. System Architecture](#2-system-architecture)
- [3. Technology Stack](#3-technology-stack)
- [4. Prerequisites](#4-prerequisites)
- [5. Installation & Configuration](#5-installation--configuration)
- [6. Running the Application](#6-running-the-application)
  - [Option 1: Docker Compose (Recommended)](#option-1-docker-compose-recommended)
  - [Option 2: Local Development Setup](#option-2-local-development-setup)
- [7. API Specifications & Endpoints](#7-api-specifications--endpoints)
- [8. Machine Learning & Empirical Evaluation](#8-machine-learning--empirical-evaluation)
- [9. Model Registry & One-Command Rollback](#9-model-registry--one-command-rollback)
- [10. Testing, Quality Assurance & CI](#10-testing-quality-assurance--ci)
- [11. Repository Structure](#11-repository-structure)
- [12. Team & Architectural Ownership](#12-team--architectural-ownership)

---

## 1. Project Overview & Problem Statement

Modern e-commerce platforms (such as Uzum Market) process hundreds of thousands of customer reviews every week. For marketplace operators and merchant partners, manual inspection of this volume is practically impossible, leading to critical operational blindspots:

- Product quality degradations or supplier defects go unnoticed until return rates spike;
- Systemic logistical bottlenecks (delivery delays, damaged packaging) are obscured in raw star ratings;
- Lack of specialized Natural Language Processing (NLP) tools capable of handling the morphology, code-switching, and orthographic inconsistencies of the Uzbek language (Latin/Cyrillic scripts and varying apostrophe encodings).

### What URI Delivers:
1. **Robust Uzbek Text Normalization:** Handles character encoding variations across Latin-script apostrophes (`'`, `ʻ`, `` ` ``, `ʼ`) to ensure deterministic tokenization.
2. **Sentiment Classification:** Accurately classifies reviews into `positive`, `neutral`, and `negative` sentiments with calibrated confidence scores.
3. **Aspect-Based Sentiment Extraction (ABSA):** Automatically identifies specific operational dimensions mentioned in the text (`delivery`, `quality`, `price`, `seller`, `packaging`, `other`) along with per-aspect polarities.
4. **Interactive Analytics Dashboard:** Provides per-product sentiment distributions over time, aspect breakdown matrices, review drill-downs, and a live scoring playground.
5. **Model Registry & Instant Rollback:** Implements immutable model version tracking allowing zero-downtime rollbacks via a single CLI command if performance degrades in production.
6. **Alerting & Anomaly Detection:** Flags products experiencing sudden spikes in negative reviews with automated Telegram notifications and built-in flood control.

---

## 2. System Architecture

The platform is designed following modular microservices principles, orchestrated via FastAPI and Docker Compose:

```
                           ┌────────────────────────┐
   Customer Reviews  ───►  │   Ingest & Storage     │ ◄── PostgreSQL 16
   (Uzum Dataset)          └───────────┬────────────┘
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                 ┌─────────────────┐       ┌─────────────────┐
                 │  sentiment-svc  │       │   aspect-svc    │
                 │  (Port: 8001)   │       │  (Port: 8002)   │
                 │  TF-IDF / BERT  │       │ Multi-label NLP │
                 └────────┬────────┘       └────────┬────────┘
                          │                         │
                          └────────────┬────────────┘
                                       ▼
                           ┌────────────────────────┐
                           │   FastAPI Gateway      │
                           │   (Port: 8000)         │
                           └───────────┬────────────┘
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                 ┌──────────────────┐      ┌─────────────────┐
                 │   Dashboard UI   │      │ Alerts Channel  │
                 │ (React/Vite 5173)│      │    (Telegram)   │
                 └──────────────────┘      └─────────────────┘
```

- **Ingest & Storage Layer:** Batches raw reviews into PostgreSQL with relational schemas (`products`, `reviews`, `predictions`) and index optimizations.
- **Microservices (`sentiment-svc` & `aspect-svc`):** Decoupled inference services operating over strictly frozen Pydantic contracts (`shared/contracts.py`).
- **Gateway API (`platform/api/app.py`):** Central aggregation layer exposing REST endpoints, aggregating analytical metrics, and proxying scoring requests.
- **Model Registry (`platform/registry`):** Immutable model storage with plain-text pointer management for one-command operational rollback.
- **Dashboard UI (`dashboard/`):** React 18 single-page application visualizing sentiment trajectories, aspect polarities, and model provenance.

---

## 3. Technology Stack

### Backend & Platform Services
- **Language:** Python 3.11 / 3.12
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (v0.110+)
- **Server:** [Uvicorn](https://www.uvicorn.org/) (v0.28+) ASGI server
- **Data Validation & Contracts:** [Pydantic v2](https://docs.pydantic.dev/)
- **Database ORM & Driver:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Psycopg 3](https://www.psycopg.org/psycopg3/)
- **Inter-Service Communication:** [HTTPX](https://www.python-httpx.org/)

### Machine Learning & NLP
- **Classical NLP:** [scikit-learn](https://scikit-learn.org/) (TfidfVectorizer, LogisticRegression)
- **Deep Learning:** [Hugging Face Transformers](https://huggingface.co/docs/transformers) & [PyTorch](https://pytorch.org/)
- **Target Language Models:** `tahrirchi/tahrirchi-bert-small` (67M parameters), `xlm-roberta-base`
- **Serialization:** Joblib

### Frontend Dashboard
- **Framework:** [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tooling:** [Vite 6](https://vite.dev/)
- **Styling:** [Tailwind CSS 3.4](https://tailwindcss.com/)
- **Visualizations:** [Recharts](https://recharts.org/) (Responsive Area & Bar charts)
- **Iconography:** Lucide React

### Infrastructure, Testing & CI/CD
- **Database:** PostgreSQL 16 (Alpine image)
- **Containerization:** Docker & Docker Compose
- **Linter & Formatter:** [Ruff](https://docs.astral.sh/ruff/) (ultra-fast code quality verification)
- **Test Framework:** [pytest](https://docs.pytest.org/) & [pytest-cov](https://pytest-cov.readthedocs.io/)
- **Continuous Integration:** GitHub Actions

---

## 4. Prerequisites

Before setting up the repository, verify that your local environment meets the following requirements:

- **Docker** and **Docker Compose** (v24.0+ recommended)
- *If running natively outside Docker:*
  - **Python 3.11** or **3.12**
  - **Node.js (v18+)** and **npm (v9+)**
  - **PostgreSQL 16** (or SQLite for lightweight local testing)
  - **Git**

---

## 5. Installation & Configuration

### 1. Clone the repository:
```bash
git clone https://github.com/BekmurodGofurov/uri.git
cd uri
```

### 2. Configure Environment Variables:
Copy the example environment configuration into `.env`:
```bash
cp .env.example .env
```

Review and adjust the parameters as needed:
```ini
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=uzum_reviews
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/uzum_reviews

# Internal Service Routing
SENTIMENT_SVC_URL=http://localhost:8001
ASPECT_SVC_URL=http://localhost:8002

# Sentiment Service Model Configuration
SENTIMENT_IMAGE=sentiment-svc:v1
SENTIMENT_PORT=8001
MODEL_PATH=models/tfidf_v1.joblib
MODEL_TYPE=tfidf
MODEL_VERSION=sentiment-v1
```

---

## 6. Running the Application

### Option 1: Docker Compose (Recommended)

To build and spin up the complete infrastructure (PostgreSQL database, Sentiment Service, Aspect Service, and Gateway API) with automatic schema initialization:

```bash
docker compose up --build
```

#### Exposed Service Endpoints:
- **FastAPI Gateway API:** `http://localhost:8000`
- **Interactive API Documentation (Swagger):** `http://localhost:8000/docs`
- **Sentiment Service Health:** `http://localhost:8001/health`
- **Aspect Service Health:** `http://localhost:8002/health`
- **PostgreSQL Database:** `localhost:5433`

To run in detached mode (background):
```bash
docker compose up -d
```

To shut down containers and networks:
```bash
docker compose down
```

---

### Option 2: Local Development Setup

#### 1. Setup Virtual Environment and Dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate

# Install platform & test dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install sentiment service dependencies
pip install -r sentiment-svc/requirements.txt
```

#### 2. Initialize Database:
If running against PostgreSQL or an in-process SQLite instance:
```bash
# SQLite quick-start:
export DATABASE_URL="sqlite:///./uzum_reviews.db"
python3 -m platform.database.connection
```

#### 3. Run Backend Services:

**Terminal 1 — Sentiment Service (Port 8001):**
```bash
cd sentiment-svc
MODEL_PATH=models/tfidf_v1.joblib MODEL_TYPE=tfidf MODEL_VERSION=sentiment-v1 \
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 — Aspect Service (Port 8002):**
```bash
# From project root:
uvicorn platform.stubs.aspect_stub:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 3 — Gateway API (Port 8000):**
```bash
# From project root:
SENTIMENT_SVC_URL=http://localhost:8001 ASPECT_SVC_URL=http://localhost:8002 \
uvicorn platform.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 4 — Dashboard UI (Port 5173):**
```bash
cd dashboard
npm install
npm run dev
```
Navigate to: `http://localhost:5173`

---

## 7. API Specifications & Endpoints

All endpoints are documented via OpenAPI and accessible interactively at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and readiness check |
| `GET` | `/api/products` | Paginated product list with overall sentiment ratios and review counts |
| `GET` | `/api/products/{id}` | Detailed product metrics, sentiment time series, and aspect distribution |
| `GET` | `/api/products/{id}/reviews` | Filterable product reviews with associated model predictions and aspect tags |
| `POST` | `/api/score` | **Live Inference Endpoint:** Ingests and scores a batch of reviews on-the-fly |

### Live Scoring Request (`POST /api/score`) Example:
```json
{
  "reviews": [
    {
      "id": "rev_test_01",
      "text": "Mahsulot juda sifatli va tez yetib keldi, menga yoqdi!",
      "rating": 5,
      "product_id": "prod_1"
    },
    {
      "id": "rev_test_02",
      "text": "Yetkazib berish juda kechikdi, quti ezilgan holda keldi.",
      "rating": 2,
      "product_id": "prod_1"
    }
  ]
}
```

Response:
```json
{
  "scored_count": 2,
  "predictions": [
    {
      "id": 1,
      "review_id": "rev_test_01",
      "sentiment_label": "positive",
      "sentiment_confidence": 0.89,
      "aspects": [
        { "aspect": "quality", "polarity": "positive" },
        { "aspect": "delivery", "polarity": "positive" }
      ],
      "model_version": "sentiment-v1;stub-aspect-v0.1.0"
    }
  ]
}
```

---

## 8. Machine Learning & Empirical Evaluation

In accordance with strict empirical requirements, all models were evaluated against disciplined baselines. Standard accuracy was rejected in favor of **Macro-F1** due to severe class imbalance in e-commerce reviews (where >80% of reviews are positive).

### Model Evaluation Benchmark:

| Model Architecture | Parameters | Val Macro-F1 | Test Macro-F1 | Deployment Status |
|---|---|---|---|---|
| **TF-IDF + Logistic Regression (v1)** | ~50k features | **0.6291** | **0.6241** | **Deployed (Winner)** |
| TahrirchiBERT-small (v1) | 67M | 0.6210 | — | Rejected |

### Per-Class Test Breakdown (TF-IDF Baseline):
| Sentiment Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Negative** | 0.71 | 0.78 | 0.75 | 9,822 |
| **Neutral** | 0.15 | 0.40 | **0.22** | 2,370 |
| **Positive** | 0.97 | 0.85 | 0.91 | 40,631 |
| **Macro Average** | **0.61** | **0.68** | **0.62** | 52,823 |

### Key Scientific Takeaway:
TahrirchiBERT achieved a higher overall accuracy (90% vs 82%) but severely underperformed on the minority `neutral` class (F1 of 0.10 vs 0.22) because standard cross-entropy fails under extreme skew. TF-IDF paired with `class_weight='balanced'` matched the deep transformer on Macro-F1 while serving predictions orders of magnitude faster with zero GPU requirements.

---

## 9. Model Registry & One-Command Rollback

The model registry uses an immutable, directory-based design with an atomic plain-text `current` pointer. Models are never overwritten in place.

```
model_registry/
  current                   ← plain text pointer: active version name
  sentiment-v1/
    meta.json               ← metadata (metrics, author, timestamp, notes)
    tfidf_v1.joblib         ← immutable artifact
  sentiment-v2/
    meta.json
    tfidf_v2.joblib
```

### One-Command Rollback CLI:
```bash
# Roll back production model to sentiment-v1:
python3 -m platform.registry rollback sentiment-v1
```

Output:
```text
Rolled back: 'sentiment-v2' → 'sentiment-v1'
Active version is now: sentiment-v1
```

### Registry CLI Commands:
```bash
# Inspect the active production model:
python3 -m platform.registry current

# List all registered versions and their metrics:
python3 -m platform.registry list

# Register a new model version:
python3 -m platform.registry register \
    --version  sentiment-v2 \
    --service  sentiment-svc \
    --type     tfidf \
    --artifact sentiment-svc/models/tfidf_v2.joblib \
    --metric   "macro-f1: 0.65" \
    --notes    "Retrained with neutral class oversampling"

# Inspect version metadata:
python3 -m platform.registry info sentiment-v1
```

---

## 10. Testing, Quality Assurance & CI

High engineering rigor was enforced from day one:
- **Test Suite:** **48 automated tests** spanning API endpoints, contracts, database models, pipeline ingestion, registry operations, and latency benchmarks.
- **Code Coverage:** **90% line coverage** on non-UI Python code (exceeding the 60% requirement).
- **Latency Benchmark:** Measured and guaranteed **p95 latency under 300ms** for batches of 32 reviews (`platform/tests/test_latency_p95.py`).

### Executing Tests:
```bash
# Run the complete test suite with coverage report:
pytest

# Verify code formatting and lint rules:
ruff check .
ruff format --check .
```

---

## 11. Repository Structure

```text
uri/
├── Dockerfile                      # Gateway API container definition
├── docker-compose.yml              # Multi-container service orchestration
├── pyproject.toml                  # Ruff & Pytest configuration
├── requirements.txt                # Production Python dependencies
├── requirements-dev.txt            # Development, testing, and CI dependencies
├── shared/                         # Frozen data contracts
│   └── contracts.py                # Pydantic schemas (ReviewIn, ScoreRequest, etc.)
├── platform/                       # Platform core services (Owned by Bekmurod)
│   ├── api/app.py                  # FastAPI Gateway routing & business logic
│   ├── database/                   # Schema migrations, engine, and ORM models
│   ├── ingest/                     # Review loading and scoring pipelines
│   ├── registry/                   # Model registry manager & one-command rollback CLI
│   ├── stubs/                      # Service stubs for isolated integration testing
│   └── tests/                      # 48 comprehensive unit & integration tests
├── sentiment-svc/                  # Sentiment classification service (Owned by Hayotbek)
│   ├── app/                        # FastAPI microservice and inference logic
│   ├── models/                     # Trained TF-IDF serialization artifacts
│   ├── preprocessing/              # Uzbek orthographic text normalizer
│   ├── training/                   # Model training and evaluation scripts
│   └── EVALUATION.md               # Empirical benchmark report
├── aspect-svc/                     # Aspect-based sentiment service (Owned by Biloliddin)
│   ├── gold_set.jsonl              # 300 expert hand-labeled Uzbek reviews
│   └── training/                   # Multi-label taxonomy and model scripts
└── dashboard/                      # Analytics UI Dashboard
    ├── src/components/             # React visual components (Charts, Aspects, Drill-down)
    └── package.json                # Frontend dependencies
```

---

## 12. Team & Architectural Ownership

The project was developed under strict collaborative rules (R1–R7) with isolated service ownership:

- **Bekmurod (Platform, Gateway & Frontend Lead):**  
  Platform skeleton, CI/CD pipelines, FastAPI Gateway, PostgreSQL database layer, Ingest pipeline, Model Registry with one-command rollback, React analytics dashboard, and platform test suite (90% coverage).
- **Hayotbek (Sentiment Service Lead):**  
  Uzbek text normalizer, deterministic dataset splitting (train/val/test), TF-IDF vs TahrirchiBERT training, Macro-F1 benchmarking, learning curve experiments, and evaluation analysis.
- **Biloliddin (Aspect Service Lead):**  
  Aspect taxonomy definition (`delivery`, `quality`, `price`, `seller`, `packaging`), hand-curated 300-sample Gold Set, Cohen's kappa consistency scoring, and multi-label ABSA architecture.

---

### 📄 License
Distributed under the MIT License. Developed for research and educational purposes.
