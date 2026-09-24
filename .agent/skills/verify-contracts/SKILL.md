---
name: verify-contracts
description: Verify that all microservice endpoints, request models, and response models conform strictly to frozen schemas in shared/contracts.py.
---

# Verify Contracts Skill

Use this skill whenever editing API routes, data ingestion logic, or service communication clients.

---

## When to Use
- Whenever modifying endpoints in `gateway/api/app.py`.
- Whenever modifying request or response handlers in `sentiment-svc/` or `aspect-svc/`.
- Whenever modifying ingestion payloads in `gateway/ingest/`.
- Prior to any cross-service integration test.

---

## Contract Rules
- `shared/contracts.py` contains the single source of truth for inter-service data models.
- Never add required fields to existing request models without backwards-compatible defaults.
- Never rename existing enum values in `Sentiment` or `Aspect`.

---

## Execution Steps

### Step 1: Inspect Shared Contract Definitions
Read `shared/contracts.py` to verify canonical definitions:
- `Sentiment`: `positive`, `neutral`, `negative`
- `Aspect`: `delivery`, `quality`, `price`, `seller`, `packaging`, `other`
- `ReviewIn`: `review_id`, `text`, `rating`
- `SentimentResponse`: `label`, `score`, `model_version`
- `AspectResponse`: `aspects`, `model_version`

### Step 2: Validate Gateway Ingest Pipeline
Run gateway ingest tests to ensure contract validation works:
```bash
pytest gateway/tests/test_ingest.py
```

### Step 3: Validate Downstream Service Responses
Verify that mock responses and actual service schemas match the expected structure:
```bash
pytest gateway/tests/test_stubs.py
pytest sentiment-svc/tests/test_routes.py
pytest aspect-svc/tests/test_routes.py
```

---

## Acceptance Criteria
- All Pydantic validation tests pass without validation errors.
- No direct code imports exist across service boundaries other than importing `shared.contracts`.
