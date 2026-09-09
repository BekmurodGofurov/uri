import os
import psycopg
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
load_dotenv(override=True)

# Base the test DB on the actual configured database URL
# so it matches the correct host, port, user, and password.
# Require DATABASE_URL from .env
base_db_url = os.getenv("DATABASE_URL")
if not base_db_url:
    raise ValueError("DATABASE_URL must be provided in .env")

parsed = urlparse(base_db_url)

# Construct admin URL to connect to the default 'postgres' database
admin_url = parsed._replace(path="/postgres", scheme="postgresql").geturl()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL must be provided in .env")

# Export it globally so all module/session fixtures can see it before function fixtures run
os.environ["TEST_DATABASE_URL"] = TEST_DATABASE_URL
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

def create_test_db():
    try:
        conn = psycopg.connect(admin_url, autocommit=True)
        try:
            conn.execute("CREATE DATABASE uzum_reviews_test")
        except psycopg.errors.DuplicateDatabase:
            pass
        finally:
            conn.close()
    except Exception as e:
        print(f"\n[Warning] Could not connect to {admin_url} to create test db.")
        print(f"Error: {e}")
        print("Tests might fail if uzum_reviews_test doesn't exist.\n")

# Ensure the DB exists before any tests run
try:
    create_test_db()
except Exception:
    pass

import pytest
from gateway.database.connection import init_db
from gateway.database.models import Base

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)
    init_db(eng)
    return eng

@pytest.fixture(scope="function")
def db_session(engine):
    # Clear tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        with engine.connect() as conn:
            conn.execute(table.delete())
            conn.commit()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function", autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

