"""Integration tests: end-to-end API flows covering requirements R1-R4."""

from conftest import ADMIN_HEADERS, VERIFIER_HEADERS

BASE = "/api/v1"
CERT = "ZW-ENG-2025-0001"
HOLDER = "Tendai Moyo"


def _register(client, headers=ADMIN_HEADERS, cert=CERT, **overrides):
    payload = {
        "certificate_number": cert,
        "holder_name": HOLDER,
        "qualification_name": "BSc Computer Science",
        "issuing_institution": "University of Zimbabwe",
        "date_issued": "2024-06-30",
    }
    payload.update(overrides)
    return client.post(f"{BASE}/qualifications", json=payload, headers=headers)


def _verify(client, cert=CERT, holder=HOLDER):
    return client.post(
        f"{BASE}/verify",
        json={"certificate_number": cert, "holder_name": holder},
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- R1: registration ------------------------------------------------------


def test_register_success(client):
    response = _register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["certificate_number"] == CERT
    assert body["status"] == "ACTIVE"


def test_register_requires_admin_role(client):
    assert _register(client, headers=VERIFIER_HEADERS).status_code == 403
    assert _register(client, headers={"X-User": "nobody"}).status_code == 403


def test_register_rejects_duplicate_certificate(client):
    assert _register(client).status_code == 201
    assert _register(client).status_code == 409


def test_register_rejects_invalid_payload(client):
    assert _register(client, cert="BAD CERT 1").status_code == 422


# --- R2: search --------------------------------------------------------------


def test_search_finds_registered_record(client):
    _register(client)
    response = client.get(
        f"{BASE}/qualifications", params={"query": "Moyo"}, headers=VERIFIER_HEADERS
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["holder_name"] == HOLDER


def test_search_returns_empty_list_when_no_match(client):
    _register(client)
    response = client.get(
        f"{BASE}/qualifications", params={"query": "Nosuchperson"}, headers=VERIFIER_HEADERS
    )
    assert response.status_code == 200
    assert response.json() == []


def test_search_requires_role(client):
    response = client.get(f"{BASE}/qualifications", params={"query": "Moyo"})
    assert response.status_code == 403


# --- R3: verification ---------------------------------------------------------


def test_verify_valid_qualification(client):
    _register(client)
    response = _verify(client)
    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "VALID"
    assert body["issuing_institution"] == "University of Zimbabwe"


def test_verify_rejects_wrong_holder_name(client):
    _register(client)
    response = _verify(client, holder="Imposter Person")
    assert response.json()["result"] == "INVALID"


def test_verify_unknown_certificate(client):
    response = _verify(client, cert="NO-SUCH-9999", holder="Anyone Name")
    assert response.json()["result"] == "INVALID"


def test_verify_rejects_revoked_qualification(client):
    registration = _register(client)
    record_id = registration.json()["id"]
    client.post(f"{BASE}/qualifications/{record_id}/revoke", headers=ADMIN_HEADERS)
    response = _verify(client)
    assert response.json()["result"] == "INVALID"
    assert "revoked" in response.json()["reason"].lower()


# --- R4: audit trail ----------------------------------------------------------


def test_audit_log_records_activity(client):
    _register(client)
    _verify(client)
    response = client.get(f"{BASE}/audit", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    actions = [entry["action"] for entry in response.json()]
    assert "REGISTRATION" in actions
    assert "VERIFY_SUCCESS" in actions


def test_audit_requires_admin(client):
    assert client.get(f"{BASE}/audit", headers=VERIFIER_HEADERS).status_code == 403
