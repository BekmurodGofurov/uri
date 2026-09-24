# CLAUDE.md

Operating guidelines and project conventions for Claude Code sessions in Uzum Review Intelligence (URI).

---

## 1. Operating Rules

1. Always ask permission before writing or editing code. Explain what and why beforehand.
2. State the exact target file path before touching it.
3. After writing code, explain the changes clearly, then request permission before moving to the next file or function.
4. Clean, fast, understandable code. No unnecessary comments. No emojis. No bloat.
5. Shorter and cleaner beats longer. Every line earns its place.
6. Top priority: privacy and security. Never commit secrets, `.env` files, or exposed tokens.
7. Check all code after writing. Report any concerns immediately.
8. Never kill, restart, or alter running background processes, services, or containers unasked.
9. No multi-agent workflows without specifying agent counts and securing explicit user consent.
10. All communication with the user must be in English.

---

## 2. Repository Commands

### Quality and Testing
- Run all tests with coverage check:
  `pytest --cov-fail-under=60`
- Run lint check:
  `ruff check .`
- Run format check:
  `ruff format --check .`
- Auto-format code:
  `ruff format .`

### Service-Specific Tests
- Gateway:
  `pytest gateway/tests/`
- Sentiment Service:
  `pytest sentiment-svc/tests/`
- Aspect Service:
  `pytest aspect-svc/tests/`

### Frontend Build
- Build React dashboard:
  `npm --prefix dashboard run build`

### Containers and Services
- Start stack:
  `docker compose up -d`
- Check container status:
  `docker compose ps`

---

## 3. Architecture and Service Rules

- Service Isolation: Do not introduce cross-service dependencies between `sentiment-svc`, `aspect-svc`, and `gateway`.
- Frozen Contracts: Schemas in `shared/contracts.py` are strictly frozen. Never edit them without repository-wide review.
- Text Normalization: All Uzbek review text must pass through `preprocessing/normalizer.py`.
- Dataset Integrity: Do not modify `split_manifest.json` or `gold_set.jsonl`.
- File Size Limit: Keep files focused, typically between 200 and 400 lines (800 lines maximum).
