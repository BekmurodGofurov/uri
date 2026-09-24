# Development and Engineering Workflow

This document details the engineering practices, version control standards, code review policies, and testing requirements for the Uzum Review Intelligence (URI) repository.

---

## 1. Service Ownership and Boundaries

To maintain clean microservice architecture, repository ownership is divided into clear functional boundaries:
- `gateway/`: Gateway API, persistence layer, and model registry.
- `sentiment-svc/`: Sentiment classification service, training pipelines, and data splits.
- `aspect-svc/`: Aspect-based sentiment analysis service, taxonomy, and inference.
- `dashboard/`: React and TypeScript user interface.
- `shared/`: Shared data contracts and Pydantic schemas.

### Cross-Service Boundaries
1. Decoupled Codebases: Services must not import code directly from one another. Inter-service coordination occurs strictly via HTTP REST endpoints and schemas in `shared/contracts.py`.
2. Frozen Contracts: Any change to models in `shared/contracts.py` requires cross-team review and mutual agreement before implementation.
3. Dependency Independence: Each service maintains its own `requirements.txt` and environment dependencies.

---

## 2. Git Branching and Workflow

### 2.1 Branching Strategy
- `main`: Production-ready branch. Code merged here must pass all automated CI checks.
- Feature branches: Created off `main` using descriptive naming:
  - `feat/<service>-<description>` (e.g., `feat/sentiment-tfidf-calibration`)
  - `fix/<service>-<description>` (e.g., `fix/gateway-cors-header`)
  - `docs/<description>` (e.g., `docs/add-deployment-runbook`)

### 2.2 Commit Messages
Use concise, conventional commit prefixes:
- `feat`: New feature or capability.
- `fix`: Bug fix.
- `test`: Adding or updating test cases.
- `refactor`: Code reorganization with no behavior change.
- `docs`: Documentation updates.
- `chore`: Dependency updates or build configuration.

---

## 3. Code Quality Gates

Before opening a pull request, all code must pass the following local validation checks.

### 3.1 Linting and Formatting
Code is checked and formatted using Ruff:
```bash
# Check code style and common errors
ruff check .

# Check code formatting conformance
ruff format --check .

# Automatically apply recommended fixes and formatting
ruff format .
```

### 3.2 Test Coverage Enforcement
Every Python microservice must maintain a minimum test coverage of 60 percent. Pull requests that lower test coverage below 60 percent will fail automated CI checks.

```bash
# Run full suite across repository with failure enforcement
pytest --cov-fail-under=60

# Run service-specific tests
pytest sentiment-svc/tests/ --cov=sentiment-svc/app --cov-fail-under=60
pytest aspect-svc/tests/ --cov=aspect-svc/app --cov-fail-under=60
pytest gateway/tests/ --cov=gateway/api --cov-fail-under=60
```

### 3.3 Frontend Verification
The React dashboard must compile without TypeScript or linting errors:
```bash
cd dashboard
npm run build
```

---

## 4. Pull Request Review Checklist

When submitting or reviewing a pull request, verify the following:
1. Architectural Separation: No cross-service imports outside of `shared/contracts.py`.
2. Coverage Maintained: Test coverage is at or above 60 percent.
3. Zero Dead Code: No unused imports, commented-out dead code, or unreferenced dependencies.
4. Security: No secrets, `.env` files, or exposed API keys are checked into Git.
5. Text Processing: Any new text handling routes through the Uzbek normalizer (`preprocessing/normalizer.py`).
