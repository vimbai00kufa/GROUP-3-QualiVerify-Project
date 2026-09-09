"""RBAC acceptance tests.

Covers the acceptance criteria for the Role-Based Access Control feature:

* Roles are represented in the system.
* Users can only access functions permitted for their role.
* Unauthorised access is rejected.
* Access-control tests exist (this file).

Structured as: role tests -> authentication tests -> per-function
authorisation matrix -> negative/security tests -> regression check.
"""

import pytest
from conftest import (
    ADMIN_HEADERS,
    NO_ROLE_HEADERS,
    REGISTRAR_HEADERS,
    STANDARD_HEADERS,
    UNKNOWN_ROLE_HEADERS,
    VERIFIER_HEADERS,
)

from app.roles import ALL_ROLES, Role

BASE = "/api/v1"

ALL_ROLE_HEADERS = {
    "administrator": ADMIN_HEADERS,
    "registrar": REGISTRAR_HEADERS,
    "verification_officer": VERIFIER_HEADERS,
    "standard_user": STANDARD_HEADERS,
}


def _register_payload(cert="ZW-RBAC-2025-0001"):
    return {
        "certificate_number": cert,
        "holder_name": "Rutendo Chikwanha",
        "qualification_name": "BSc Information Systems",
        "issuing_institution": "University of Zimbabwe",
        "date_issued": "2024-06-30",
    }


def _register(client, headers, cert="ZW-RBAC-2025-0001"):
    return client.post(f"{BASE}/qualifications", json=_register_payload(cert), headers=headers)


# ---------------------------------------------------------------------------
# 1. Role tests -- all four roles exist and are distinguishable
# ---------------------------------------------------------------------------


def test_all_four_roles_exist():
    assert ALL_ROLES == {
        Role.ADMINISTRATOR,
        Role.REGISTRAR,
        Role.VERIFICATION_OFFICER,
        Role.STANDARD_USER,
    }
    assert len(ALL_ROLES) == 4


@pytest.mark.parametrize("role_name,headers", ALL_ROLE_HEADERS.items())
def test_role_can_be_assigned_via_header_and_is_accepted(client, role_name, headers):
    """Each of the four roles authenticates successfully (search is open to all)."""
    response = client.get(f"{BASE}/qualifications", params={"query": "xx"}, headers=headers)
    assert response.status_code == 200, f"{role_name} should be authenticated for search"


# ---------------------------------------------------------------------------
# 2. Authentication tests -- unauthenticated / unrecognised role is rejected
# ---------------------------------------------------------------------------


def test_unauthenticated_request_rejected_on_every_protected_endpoint(client):
    search_url = f"{BASE}/qualifications"
    revoke_url = f"{BASE}/qualifications/1/revoke"
    assert _register(client, NO_ROLE_HEADERS).status_code == 401
    assert (
        client.get(search_url, params={"query": "xx"}, headers=NO_ROLE_HEADERS).status_code == 401
    )
    assert client.get(f"{BASE}/audit", headers=NO_ROLE_HEADERS).status_code == 401
    assert client.post(revoke_url, headers=NO_ROLE_HEADERS).status_code == 401


def test_unrecognised_role_is_rejected_as_unauthenticated(client):
    """A role string that isn't one of the four is treated as an authentication failure."""
    assert _register(client, UNKNOWN_ROLE_HEADERS).status_code == 401
    assert client.get(f"{BASE}/audit", headers=UNKNOWN_ROLE_HEADERS).status_code == 401


def test_authenticated_role_can_access_its_permitted_functions(client):
    assert client.get(f"{BASE}/audit", headers=ADMIN_HEADERS).status_code == 200


# ---------------------------------------------------------------------------
# 3. Authorisation matrix -- every role against every protected function
# ---------------------------------------------------------------------------

# (endpoint label, call) -> {role: expected_status}
REGISTER_MATRIX = {
    Role.ADMINISTRATOR: 201,
    Role.REGISTRAR: 201,
    Role.VERIFICATION_OFFICER: 403,
    Role.STANDARD_USER: 403,
}

SEARCH_MATRIX = {
    Role.ADMINISTRATOR: 200,
    Role.REGISTRAR: 200,
    Role.VERIFICATION_OFFICER: 200,
    Role.STANDARD_USER: 200,
}

REVOKE_MATRIX = {
    Role.ADMINISTRATOR: 200,
    Role.REGISTRAR: 403,
    Role.VERIFICATION_OFFICER: 403,
    Role.STANDARD_USER: 403,
}

AUDIT_MATRIX = {
    Role.ADMINISTRATOR: 200,
    Role.REGISTRAR: 403,
    Role.VERIFICATION_OFFICER: 200,
    Role.STANDARD_USER: 403,
}

_HEADERS_BY_ROLE = {
    Role.ADMINISTRATOR: ADMIN_HEADERS,
    Role.REGISTRAR: REGISTRAR_HEADERS,
    Role.VERIFICATION_OFFICER: VERIFIER_HEADERS,
    Role.STANDARD_USER: STANDARD_HEADERS,
}


@pytest.mark.parametrize("role,expected_status", REGISTER_MATRIX.items())
def test_register_authorisation_matrix(client, role, expected_status):
    response = _register(client, _HEADERS_BY_ROLE[role], cert=f"ZW-REG-{role[:4].upper()}-0001")
    assert response.status_code == expected_status


@pytest.mark.parametrize("role,expected_status", SEARCH_MATRIX.items())
def test_search_authorisation_matrix(client, role, expected_status):
    response = client.get(
        f"{BASE}/qualifications", params={"query": "xx"}, headers=_HEADERS_BY_ROLE[role]
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize("role,expected_status", REVOKE_MATRIX.items())
def test_revoke_authorisation_matrix(client, role, expected_status):
    created = _register(client, ADMIN_HEADERS, cert=f"ZW-REV-{role[:4].upper()}-0001")
    record_id = created.json()["id"]
    revoke_url = f"{BASE}/qualifications/{record_id}/revoke"
    response = client.post(revoke_url, headers=_HEADERS_BY_ROLE[role])
    assert response.status_code == expected_status


@pytest.mark.parametrize("role,expected_status", AUDIT_MATRIX.items())
def test_audit_authorisation_matrix(client, role, expected_status):
    response = client.get(f"{BASE}/audit", headers=_HEADERS_BY_ROLE[role])
    assert response.status_code == expected_status


def test_verify_is_public_for_every_role_and_for_no_role(client):
    """Verification (R3) is intentionally outside the role matrix -- see routes.py docstring."""
    _register(client, ADMIN_HEADERS, cert="ZW-PUB-0001")
    payload = {"certificate_number": "ZW-PUB-0001", "holder_name": "Rutendo Chikwanha"}
    for headers in (*_HEADERS_BY_ROLE.values(), NO_ROLE_HEADERS, {}):
        assert client.post(f"{BASE}/verify", json=payload, headers=headers).status_code == 200


# ---------------------------------------------------------------------------
# 4. Negative / security tests
# ---------------------------------------------------------------------------


def test_standard_user_cannot_access_administrator_functions(client):
    assert client.get(f"{BASE}/audit", headers=STANDARD_HEADERS).status_code == 403
    assert _register(client, STANDARD_HEADERS).status_code == 403


def test_registrar_cannot_manage_audit_or_revoke(client):
    """Registrar has no 'manage users/system' style privileges in this system."""
    assert client.get(f"{BASE}/audit", headers=REGISTRAR_HEADERS).status_code == 403
    created = _register(client, ADMIN_HEADERS, cert="ZW-NOMANAGE-0001")
    record_id = created.json()["id"]
    revoke_url = f"{BASE}/qualifications/{record_id}/revoke"
    assert client.post(revoke_url, headers=REGISTRAR_HEADERS).status_code == 403


def test_verification_officer_cannot_register_or_revoke(client):
    """A Verification Officer can verify/search/audit, but cannot create or revoke records."""
    assert _register(client, VERIFIER_HEADERS).status_code == 403
    created = _register(client, ADMIN_HEADERS, cert="ZW-NOREVOKE-0001")
    record_id = created.json()["id"]
    revoke_url = f"{BASE}/qualifications/{record_id}/revoke"
    assert client.post(revoke_url, headers=VERIFIER_HEADERS).status_code == 403


def test_role_cannot_be_self_escalated_via_request_body(client):
    """Sending an 'administrator' role/claim in the JSON body must not grant privilege;
    only the (server-trusted-in-this-demo) X-Role header is consulted."""
    payload = {**_register_payload("ZW-ESCALATE-0001"), "role": "administrator", "is_admin": True}
    response = client.post(f"{BASE}/qualifications", json=payload, headers=STANDARD_HEADERS)
    assert response.status_code == 403


def test_unauthenticated_users_cannot_access_any_protected_endpoint(client):
    for method, path in (
        ("POST", f"{BASE}/qualifications"),
        ("GET", f"{BASE}/qualifications?query=xx"),
        ("GET", f"{BASE}/audit"),
        ("POST", f"{BASE}/qualifications/1/revoke"),
    ):
        response = client.request(method, path)
        assert response.status_code == 401, f"{method} {path} should require authentication"


# ---------------------------------------------------------------------------
# 5. Regression -- RBAC must not break existing R1-R4 functionality
# ---------------------------------------------------------------------------


def test_full_workflow_still_works_end_to_end_with_correct_roles(client):
    created = _register(client, ADMIN_HEADERS, cert="ZW-E2E-0001")
    assert created.status_code == 201

    search = client.get(
        f"{BASE}/qualifications", params={"query": "Rutendo"}, headers=STANDARD_HEADERS
    )
    assert search.status_code == 200
    assert len(search.json()) == 1

    verify = client.post(
        f"{BASE}/verify",
        json={"certificate_number": "ZW-E2E-0001", "holder_name": "Rutendo Chikwanha"},
    )
    assert verify.status_code == 200
    assert verify.json()["result"] == "VALID"

    audit = client.get(f"{BASE}/audit", headers=ADMIN_HEADERS)
    assert audit.status_code == 200
    assert any(entry["action"] == "REGISTRATION" for entry in audit.json())
