import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database.connection import get_db
from routers.health import router as health_router


@pytest.fixture()
def client(db_session):
    """A minimal FastAPI app with just the health router, wired to the
    in-memory test database instead of the real Postgres one."""
    app = FastAPI()
    app.include_router(health_router)
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


def test_health_returns_ok_when_db_is_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
