"""Shared fixtures: a fresh app instance with a temporary database per test."""

import pytest
from fastapi.testclient import TestClient

from app import create_app
from app.config import Settings

ADMIN_HEADERS = {"X-Role": "admin", "X-User": "admin@univ.example"}
VERIFIER_HEADERS = {"X-Role": "verifier", "X-User": "verifier@univ.example"}


@pytest.fixture()
def client(tmp_path):
    """A TestClient against a brand-new app and database (full isolation)."""
    settings = Settings(
        database_url=f"sqlite:///{tmp_path}/test_qvs.db",
        hmac_secret_key="test-secret-key",
    )
    app = create_app(settings=settings)
    with TestClient(app) as test_client:
        yield test_client
    app.state.engine.dispose()
