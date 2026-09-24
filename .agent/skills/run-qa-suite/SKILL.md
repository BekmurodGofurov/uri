---
name: run-qa-suite
description: Run Ruff linting, formatting check, and Pytest coverage across the monorepo with 60 percent minimum coverage enforcement.
---

# Run QA Suite Skill

Use this skill whenever Python code is modified, before committing changes, or before preparing a release.

---

## When to Use
- After modifying or adding Python files in `gateway/`, `sentiment-svc/`, `aspect-svc/`, or `shared/`.
- Prior to opening a pull request or submitting code for review.
- When verifying that test coverage meets the repository threshold.

---

## Execution Steps

### Step 1: Check Linting and Syntax
Run Ruff across the entire repository to detect syntax issues, unused imports, or style violations:
```bash
ruff check .
```
If violations are reported, inspect them and fix them. For auto-fixable issues:
```bash
ruff check --fix .
```

### Step 2: Check Code Formatting
Verify that all files comply with repository formatting standards:
```bash
ruff format --check .
```
To reformat automatically:
```bash
ruff format .
```

### Step 3: Run Full Test Suite with Coverage
Run Pytest across all test suites, enforcing a minimum of 60 percent coverage:
```bash
pytest --cov-fail-under=60
```

### Step 4: Run Service-Specific Verification (If isolated)
When testing a specific microservice in isolation:
- Gateway:
  `pytest gateway/tests/ --cov=gateway/api --cov-fail-under=60`
- Sentiment Service:
  `pytest sentiment-svc/tests/ --cov=sentiment-svc/app --cov-fail-under=60`
- Aspect Service:
  `pytest aspect-svc/tests/ --cov=aspect-svc/app --cov-fail-under=60`

---

## Acceptance Criteria
- Ruff check exits with zero errors.
- Ruff format check exits with zero modifications needed.
- All unit and integration tests pass.
- Overall code coverage is at or above 60 percent.
