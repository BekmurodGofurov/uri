"""
p95 Latency Benchmark — platform/tests/test_latency_p95.py

Requirement (Section 7): p95 latency under 300ms for a batch of 32 reviews,
measured and recorded.

This test:
  1. Sends 50 batches of 32 reviews to the gateway /api/score endpoint.
  2. Calculates the p95 of the response times.
  3. Asserts p95 < 300ms.
  4. Prints a summary table to stdout (always visible in CI logs).

The test uses the in-process FastAPI TestClient (no network), which gives
a realistic measure of processing time excluding actual network overhead.
"""

import statistics
import time
from gateway.api.app import app
from gateway.database.models import Base
from gateway.stubs.aspect_stub import app as aspect_app
from gateway.stubs.sentiment_stub import app as sentiment_app

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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
    """Build a /api/score payload with BATCH_SIZE reviews."""
    return {
        "reviews": [
            {
                "id": f"lat_{batch_idx}_{i}",
                "text": f"Mahsulot {batch_idx}-{i} haqida fikr: a'lo sifat, tez yetkazildi.",
                "rating": (i % 5) + 1,
                "product_id": f"prod_{i % 5 + 1}",
            }
            for i in range(BATCH_SIZE)
        ]
    }


def test_p95_latency_under_300ms(gateway_client: TestClient):
    """
    Sends NUM_ITERATIONS batches of BATCH_SIZE reviews and asserts that
    the p95 wall-clock time per batch is below P95_THRESHOLD_MS.
    """
    latencies_ms: list[float] = []

    # Warm-up: 3 calls to avoid cold-start skew
    for w in range(3):
        r = gateway_client.post("/api/score", json=_build_batch(batch_idx=9900 + w))
        assert r.status_code == 200, f"Warm-up call failed: {r.text}"

    # Measured runs
    for i in range(NUM_ITERATIONS):
        payload = _build_batch(batch_idx=i)
        t0 = time.perf_counter()
        response = gateway_client.post("/api/score", json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        assert response.status_code == 200, (
            f"Batch {i} failed with {response.status_code}: {response.text}"
        )
        latencies_ms.append(elapsed_ms)

    # Stats
    sorted_lat = sorted(latencies_ms)
    p50 = statistics.median(latencies_ms)
    p95 = sorted_lat[int(len(latencies_ms) * 0.95)]
    p99 = sorted_lat[min(int(len(latencies_ms) * 0.99), len(latencies_ms) - 1)]
    mean = statistics.mean(latencies_ms)
    max_ms = max(latencies_ms)

    # Always print — visible in CI logs regardless of pass/fail
    print(
        f"\n{'=' * 55}\n"
        f"  Latency benchmark — batch_size={BATCH_SIZE}, n={NUM_ITERATIONS}\n"
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
