# Local Development Setup

This guide provides instructions for setting up the Uzum Review Intelligence (URI) environment on your local development machine.

---

## 1. Prerequisites

Ensure the following tools are installed:
- Python: Version 3.11 or 3.12.
- Node.js: Version 20 LTS or higher, with npm.
- Docker and Docker Compose: Required for multi-container development.
- PostgreSQL 16: Optional if running database directly without Docker.

---

## 2. Environment Configuration

Copy the example environment file to create your local `.env`:

```bash
cp .env.example .env
```

### Key Environment Variables
- `POSTGRES_USER`: Database username (default: `postgres`).
- `POSTGRES_PASSWORD`: Database password (default: `postgres`).
- `POSTGRES_DB`: Database name (default: `uzum_reviews`).
- `POSTGRES_PORT`: Exposed host port for PostgreSQL (default: `5433` to prevent conflicts with local Postgres).
- `DATABASE_URL`: Connection string formatted for SQLAlchemy with psycopg3:
  `postgresql+psycopg://postgres:postgres@localhost:5433/uzum_reviews`
- `SENTIMENT_SVC_URL`: URL to sentiment service (`http://localhost:8001` locally, `http://sentiment-svc:8001` in Docker).
- `ASPECT_SVC_URL`: URL to aspect service (`http://localhost:8002` locally, `http://aspect-svc:8002` in Docker).
- `API_KEY`: Secret key used for authenticating write operations on the gateway.
- `CORS_ORIGINS`: Comma-separated list of allowed origins (e.g. `http://localhost:5173,http://localhost:3000`).

---

## 3. Running with Docker Compose (Recommended)

To start the database and all backend services concurrently:

```bash
# Build and start services in the background
docker compose up -d

# Verify that all containers are healthy
docker compose ps
```

Services are exposed at the following URLs:
- Gateway API: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`
- Sentiment Service: `http://localhost:8001`
- Aspect Service: `http://localhost:8002`

---

## 4. Running Services Locally Without Docker

If running services directly in separate terminal windows:

### Step 1: Create and Activate Virtual Environment
```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Step 2: Start PostgreSQL
Ensure PostgreSQL is running locally on port 5433 (or update `DATABASE_URL` in `.env`).

### Step 3: Run Sentiment Service
```bash
cd sentiment-svc
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 4: Run Aspect Service
```bash
cd aspect-svc
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Step 5: Run Gateway Service
From the repository root:
```bash
uvicorn gateway.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Run React Dashboard
```bash
cd dashboard
npm install
npm run dev
```
The dashboard interface will be accessible at `http://localhost:5173`.

---

## 5. Seeding Data

To populate the local PostgreSQL database with reviews from HuggingFace dataset:

```bash
python scripts/fast_postgres_ingest.py --limit 1000
```
This command downloads reviews, applies text normalization, executes inference through both services, and populates the database tables.
