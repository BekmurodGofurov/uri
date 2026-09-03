import os
from collections.abc import Generator
from platform.database.models import Base

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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


def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    engine = get_engine(database_url)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
