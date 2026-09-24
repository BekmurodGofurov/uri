# Agent Guidelines for Uzum Review Intelligence (URI)

This repository is a multi-service platform for analyzing Uzbek-language e-commerce product reviews. All AI coding assistants working in this repository must follow the instructions below.

---

## 1. System Architecture and Service Boundaries

The monorepo contains four main components:
- `gateway/`: Central API gateway, review ingestion, PostgreSQL persistence, and model registry management (Port 8000).
- `sentiment-svc/`: Sentiment classification service using TF-IDF and balanced Logistic Regression (Port 8001).
- `aspect-svc/`: Aspect-based sentiment extraction service classifying categories and polarities (Port 8002).
- `dashboard/`: React and TypeScript frontend dashboard for analytics and review inspection (Port 5173 / 3000).
- `shared/`: Frozen cross-service contracts and Pydantic schemas in `shared/contracts.py`.

### Boundary Rules
- Contracts in `shared/contracts.py` are frozen. Never alter payload models or field names without cross-service review.
- Keep services decoupled. Do not import code directly between `sentiment-svc`, `aspect-svc`, and `gateway`. Cross-service communication must happen strictly via HTTP APIs or schemas in `shared/`.
- Respect service ownership boundaries. Each service maintains its own dependencies, tests, and Docker configuration.

---

## 2. Standard Commands

### Linting and Formatting
- Check lint rules across the repo:
  `ruff check .`
- Check code formatting:
  `ruff format --check .`
- Auto-format code:
  `ruff format .`

### Testing and Coverage
- Run all tests with minimum 60 percent coverage enforcement:
  `pytest --cov-fail-under=60`
- Run sentiment service tests:
  `pytest sentiment-svc/tests/`
- Run aspect service tests:
  `pytest aspect-svc/tests/`
- Run gateway tests:
  `pytest gateway/tests/`

### Frontend Build
- Install dependencies:
  `npm --prefix dashboard ci`
- Type-check and build dashboard:
  `npm --prefix dashboard run build`

### Local Multi-Container Environment
- Start all services:
  `docker compose up -d`
- Check running container status:
  `docker compose ps`
- View gateway logs:
  `docker compose logs -f gateway`

---

## 3. Engineering and Code Quality Standards

- Minimum Test Coverage: Every non-UI Python service must maintain at least 60 percent test coverage. Never decrease coverage below existing levels.
- Uzbek Text Normalization: All incoming text processing must route through the Uzbek normalizer (`preprocessing/normalizer.py`) to handle apostrophe variations and script consistency.
- ML Reproducibility:
  - Do not modify committed split manifests (`split_manifest.json`) or locked test sets (`gold_set.jsonl`).
  - Model evaluation must beat the baseline Macro-F1 floor before any candidate model is registered.
- Clean Code:
  - Keep files small and focused (typically 200 to 400 lines).
  - Explicit type annotations on all public functions and routes.
  - Zero unused imports or dead code.

---

## 4. Safety and Security Rules

- Never commit `.env` files or hardcoded API keys. Use `.env.example` for environment variable templates.
- Never modify or delete persistent database volumes unasked.
- Never terminate or restart running servers or background jobs without explicit user permission.
- Always check generated code against linting and tests before marking any task complete.
