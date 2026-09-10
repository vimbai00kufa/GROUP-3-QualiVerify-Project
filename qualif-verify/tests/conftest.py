"""QVS - Test fixtures (skeleton, simple only)."""

import pytest
from fastapi.testclient import TestClient

from app import create_app


@pytest.fixture
def client():
    """Fresh test client - skeleton only."""
    app = create_app()
    return TestClient(app)
