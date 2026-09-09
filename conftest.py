"""Shared fixtures: a fresh app instance with a temporary database per test."""

import pytest
from fastapi.testclient import TestClient

from app import create_app
from app.config import Settings

# RBAC test headers: one per role (see app/roles.py::Role and docs/RBAC.md).
ADMIN_HEADERS = {"X-Role": "administrator", "X-User": "admin@univ.example"}
REGISTRAR_HEADERS = {"X-Role": "registrar", "X-User": "registrar@univ.example"}
VERIFIER_HEADERS = {"X-Role": "verification_officer", "X-User": "verifier@univ.example"}
STANDARD_HEADERS = {"X-Role": "standard_user", "X-User": "student@univ.example"}
NO_ROLE_HEADERS = {"X-User": "nobody@univ.example"}  # authenticated identity, no role
UNKNOWN_ROLE_HEADERS = {"X-Role": "superuser", "X-User": "hacker@univ.example"}


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
