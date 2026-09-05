import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gateway.database.models import Base

load_dotenv()

DEFAULT_DATABASE_URL = "sqlite:///./uzum_reviews.db"


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        return DEFAULT_DATABASE_URL
    # Ensure postgresql:// is compatible with sqlalchemy psycopg driver
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine(database_url: str | None = None):
    url = database_url or get_database_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args)


def init_db(engine=None) -> None:
    target_engine = engine or get_engine()
    Base.metadata.create_all(bind=target_engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session backed by a **shared** engine singleton.

    The engine and session factory are created once (on first call) and reused
    for the lifetime of the process, avoiding the cost — and connection-pool
    leak — of calling ``create_engine()`` on every HTTP request.
    """
    session = _get_session_factory()()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Module-level singleton for the SQLAlchemy engine / session factory.
# Tests never touch these directly — they override ``get_db`` via
# ``app.dependency_overrides`` which is the canonical FastAPI pattern.
# ---------------------------------------------------------------------------
_engine = None
_SessionLocal = None


def _get_session_factory():
    """Return (and lazily create) the shared ``sessionmaker``."""
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal

