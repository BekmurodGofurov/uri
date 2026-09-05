"""
Gateway In-Process Overhead Benchmark — gateway/tests/test_latency_p95.py

NOTE ON SCOPE:
  This test measures the gateway's internal framework overhead:
    ✓ FastAPI routing and dependency injection
    ✓ Pydantic request & response validation / serialization
    ✓ JSON serialization/deserialization

  This test DOES NOT measure:
    ✗ Real network latency (in-process TestClient is used)
    ✗ Real ML model inference time (fast in-process stubs are used)
    ✗ Production PostgreSQL latency (in-memory SQLite is used)

For end-to-end latency benchmarks with real models and network overhead,
refer to BENCHMARKS.md and run benchmarks against the full docker compose stack.
"""

import statistics
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from gateway.api.app import app
from gateway.database.models import Base
from gateway.stubs.aspect_stub import app as aspect_app
from gateway.stubs.sentiment_stub import app as sentiment_app

P95_THRESHOLD_MS = 300.0  # hard limit from requirements
BATCH_SIZE = 32  # reviews per call (matches requirement)
NUM_ITERATIONS = 50  # number of batches to measure


@pytest.fixture(scope="module")
def gateway_client():
    """
    Spin up the gateway against an in-memory SQLite DB and stub ML services.
    Dependency overrides ensure no real network or disk I/O.
    """
    from gateway.api.app import get_db, get_ml_clients

    # Isolated in-memory SQLite DB with all tables created
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # In-process TestClients for the stub ML services (no HTTP)
    sent_tc = TestClient(sentiment_app)
    asp_tc = TestClient(aspect_app)

    def override_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    def override_ml():
        yield sent_tc, asp_tc  # type: ignore[misc]

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ml_clients] = override_ml

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def _build_batch(batch_idx: int) -> dict:
    """Build a /api/score/preview payload with BATCH_SIZE reviews."""
    return {
        "reviews": [
            {
                "text": f"Mahsulot {batch_idx}-{i} haqida fikr: a'lo sifat, tez yetkazildi.",
                "rating": (i % 5) + 1,
            }
            for i in range(BATCH_SIZE)
        ]
    }


def test_gateway_overhead_p95(gateway_client: TestClient):
    """
    Sends NUM_ITERATIONS batches of BATCH_SIZE reviews and asserts that
    the gateway overhead p95 wall-clock time per batch is below P95_THRESHOLD_MS.
    """
    latencies_ms: list[float] = []

    # Warm-up: 3 calls to avoid cold-start skew
    for w in range(3):
        r = gateway_client.post("/api/score/preview", json=_build_batch(batch_idx=9900 + w))
        assert r.status_code == 200, f"Warm-up call failed: {r.text}"

    # Measured runs
    for i in range(NUM_ITERATIONS):
        payload = _build_batch(batch_idx=i)
        t0 = time.perf_counter()
        response = gateway_client.post("/api/score/preview", json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        assert response.status_code == 200, (
            f"Batch {i} failed with {response.status_code}: {response.text}"
        )
        latencies_ms.append(elapsed_ms)

    # Stats using statistics.quantiles (mathematically defensible percentile)
    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=100)[94]
    p99 = statistics.quantiles(latencies_ms, n=100)[98]
    mean = statistics.mean(latencies_ms)
    max_ms = max(latencies_ms)

    # Always print — visible in CI logs regardless of pass/fail
    print(
        f"\n{'=' * 55}\n"
        f"  Gateway Overhead benchmark — batch_size={BATCH_SIZE}, n={NUM_ITERATIONS}\n"
        f"{'=' * 55}\n"
        f"  Mean  : {mean:6.1f} ms\n"
        f"  p50   : {p50:6.1f} ms\n"
        f"  p95   : {p95:6.1f} ms  (threshold: {P95_THRESHOLD_MS} ms)\n"
        f"  p99   : {p99:6.1f} ms\n"
        f"  Max   : {max_ms:6.1f} ms\n"
        f"{'=' * 55}"
    )

    assert p95 < P95_THRESHOLD_MS, (
        f"p95 latency {p95:.1f}ms exceeds {P95_THRESHOLD_MS}ms threshold (batch_size={BATCH_SIZE})"
    )
