"""
Shared pytest fixtures for the whole test suite.

Key ideas:
- The app's code lives in `src/` and uses absolute imports like
  `from database.connection import get_db` (no top-level package name).
  So we add `src/` to sys.path here, once, for every test.
- Tests never touch the real Postgres database. `db_session` spins up a
  fresh in-memory SQLite database per test, using the *same* SQLAlchemy
  models (`Base.metadata`) the app defines. That keeps tests fast,
  isolated, and safe to run in any order / in parallel.
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

from database.define_tables import Base, ModelMetadata, ModelDeployment, APIKey

# The `Inference` table uses Postgres's JSONB column type, which SQLite
# doesn't know how to create. Tests use SQLite for speed/isolation, so we
# teach SQLAlchemy to treat JSONB as plain JSON only when compiling for
# the sqlite dialect. This doesn't touch app code or Postgres behavior.
@compiles(JSONB, "sqlite")
def _compile_jsonb_as_json_for_sqlite(type_, compiler, **kw):
    return "JSON"


@pytest.fixture()
def db_session():
    """A fresh, isolated in-memory SQLite session for a single test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def make_model_metadata(db_session):
    """Factory to insert a ModelMetadata row and return it."""

    def _make(model_id="model-1", **overrides):
        defaults = dict(
            id=model_id,
            trained_on="dataset-v1",
            trained_time="2026-01-01T00:00:00",
            precision=0.9,
            recall=0.8,
            f1=0.85,
            auc=0.95,
            pr_auc=0.9,
        )
        defaults.update(overrides)
        row = ModelMetadata(**defaults)
        db_session.add(row)
        db_session.commit()
        db_session.refresh(row)
        return row

    return _make


@pytest.fixture()
def make_deployment(db_session):
    """Factory to insert a ModelDeployment row and return it."""

    def _make(model_id="model-1", is_active=True):
        row = ModelDeployment(model_id=model_id, is_active=is_active)
        db_session.add(row)
        db_session.commit()
        db_session.refresh(row)
        return row

    return _make


@pytest.fixture()
def make_api_key(db_session):
    """Factory to insert an APIKey row (already hashed) and return it."""

    def _make(client_name="test-client", key_hash="deadbeef", scopes=None, revoked=False):
        row = APIKey(
            client_name=client_name,
            key_hash=key_hash,
            scopes=scopes or [],
            revoked=revoked,
        )
        db_session.add(row)
        db_session.commit()
        db_session.refresh(row)
        return row

    return _make


@pytest.fixture()
def sample_transactions_df():
    """A tiny, valid transactions DataFrame with a binary target column."""
    return pd.DataFrame(
        {
            "amount": [10.0, 250.0, 5.0, 999.0],
            "hour": [1, 14, 3, 23],
            "Class": [0, 0, 0, 1],
        }
    )
