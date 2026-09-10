"""QVS - Integration tests (skeleton, simple texts only)."""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "skeleton" in response.json()["message"]


def test_r1_register(client):
    response = client.post("/api/v1/qualifications")
    assert response.status_code == 200
    assert "R1" in response.json()["message"]


def test_r2_search(client):
    response = client.get("/api/v1/qualifications")
    assert response.status_code == 200
    assert "R2" in response.json()["message"]


def test_r3_verify(client):
    response = client.post("/api/v1/verify")
    assert response.status_code == 200
    assert "R3" in response.json()["message"]


def test_r4_audit(client):
    response = client.get("/api/v1/audit")
    assert response.status_code == 200
    assert "R4" in response.json()["message"]
