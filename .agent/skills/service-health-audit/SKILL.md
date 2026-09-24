---
name: service-health-audit
description: Audit multi-container Docker Compose health, poll microservice health endpoints, and check database connectivity.
---

# Service Health Audit Skill

Use this skill when launching services, testing container orchestration, or troubleshooting communication between microservices.

---

## When to Use
- After running `docker compose up -d`.
- When diagnosing HTTP 502 or connection refused errors.
- Prior to demonstrating the multi-service system.

---

## Health Check Matrix

| Service | Container Name | Health Endpoint | Expected Response |
|---|---|---|---|
| PostgreSQL | `uri-postgres` | Port 5433 (Host) / 5432 (Internal) | `pg_isready` exit code 0 |
| Gateway | `uri-gateway` | `http://localhost:8000/api/health` | `{"status":"healthy","database":"connected",...}` |
| Sentiment Service | `uri-sentiment-svc` | `http://localhost:8001/health` | `{"status":"ok"}` |
| Aspect Service | `uri-aspect-svc` | `http://localhost:8002/health` | `{"status":"ok"}` |
| Dashboard | `uri-dashboard` | `http://localhost:5173` | HTTP 200 OK |

---

## Execution Steps

### Step 1: Check Docker Container State
Verify that all containers are running and reported as healthy:
```bash
docker compose ps
```

### Step 2: Probe Gateway Health Endpoint
Test whether the Gateway can connect to PostgreSQL and downstream services:
```bash
curl -s http://localhost:8000/api/health
```

### Step 3: Check Microservice Health
Inspect microservices individually:
```bash
curl -s http://localhost:8001/health
curl -s http://localhost:8002/health
```

### Step 4: Test Ad-Hoc Scoring Pipeline
Execute a sample test query to ensure end-to-end inference works:
```bash
curl -s -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"text": "Yetkazib berish juda tez, mahsulot ajoyib."}'
```

---

## Acceptance Criteria
- All containers show status `Up` or `healthy`.
- Gateway `/api/health` reports status `healthy` with `database: connected`.
- Sample scoring request returns both sentiment prediction and extracted aspects with 200 OK.
