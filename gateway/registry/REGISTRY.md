# Model Registry

Versioned model storage with **one-command rollback** for the Uzum Review Intelligence platform.

## Design

A versioned directory tree with a plain-text `current` pointer file.
This is the "versioned directory + pointer file" approach explicitly listed as acceptable in the project requirements.
No external tracking server is needed.

```
model_registry/
  current                   ← plain text: active version name
  sentiment-v1/
    meta.json               ← version metadata
    tfidf_v1.joblib         ← copied artifact (never overwritten)
  sentiment-v2/
    meta.json
    tfidf_v2.joblib
```

**Key property:** model files are never overwritten.  
Each `register` call creates a new directory. `rollback` only changes the `current` pointer.

## One-command rollback

```bash
python -m gateway.registry rollback sentiment-v1
```

Output:
```
Rolled back: 'sentiment-v2' → 'sentiment-v1'
Active version is now: sentiment-v1
```

> [!IMPORTANT]
> **Rollback haqida muhim eslatma:**
> Rollback buyrug'i faqat `current` pointer faylini yangilaydi. Ishlab turgan `sentiment-svc` modeli yangilanishi uchun xizmat yangi `MODEL_PATH` bilan qayta ishga tushirilishi (restart) kerak:
> ```bash
> docker compose restart sentiment-svc
> ```

## All CLI commands

```bash
# Show active version and its metadata
python -m gateway.registry current

# List all registered versions (sorted by registration time)
python -m gateway.registry list

# Register a new model artifact (file or directory)
python -m gateway.registry register \
    --version  sentiment-v2 \
    --service  sentiment-svc \
    --type     tfidf \
    --artifact sentiment-svc/models/tfidf_v2.joblib \
    --metric   "macro-f1: 0.65" \
    --notes    "Retrained with augmented neutral class"

# Roll back to a previous version
python -m gateway.registry rollback sentiment-v1

# Show full metadata for a version
python -m gateway.registry info sentiment-v1
```

## Environment variable

| Variable | Default | Description |
|---|---|---|
| `REGISTRY_ROOT` | `./model_registry` | Path to the registry root directory |

Set `REGISTRY_ROOT` in docker-compose or `.env` to point to a volume mount.

## Registering the current sentiment model

The TF-IDF model (`sentiment-v1`) is already trained. Register it:

```bash
python -m gateway.registry register \
    --version  sentiment-v1 \
    --service  sentiment-svc \
    --type     tfidf \
    --artifact sentiment-svc/models/tfidf_v1.joblib \
    --metric   "macro-f1: 0.6241 (test set)"
```

## Demo rollback (Day-7 demo script)

```bash
# 1. Show current state
python -m gateway.registry current

# 2. Register a hypothetical v2
python -m gateway.registry register \
    --version sentiment-v2 \
    --service sentiment-svc \
    --type    tfidf \
    --artifact sentiment-svc/models/tfidf_v1.joblib \
    --metric  "macro-f1: 0.64 (demo)"

# 3. Confirm v2 is active
python -m gateway.registry list

# 4. Simulate bad deploy → roll back
python -m gateway.registry rollback sentiment-v1

# 5. Confirm rollback succeeded
python -m gateway.registry current
```

## Python API

```python
from gateway.registry import ModelRegistry

reg = ModelRegistry()                              # uses ./model_registry

reg.register("sentiment-v2", "sentiment-svc",
             "tfidf", "models/tfidf_v2.joblib",
             headline_metric="macro-f1: 0.65")

reg.current()          # → "sentiment-v2"
reg.list_versions()    # → ["sentiment-v1", "sentiment-v2"]
reg.rollback("sentiment-v1")
reg.current()          # → "sentiment-v1"

path = reg.artifact_path(reg.current())  # Path to the active model file
```

