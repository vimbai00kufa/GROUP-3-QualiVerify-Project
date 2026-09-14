"""Unit tests for the verification service (no database, no HTTP)."""

from datetime import date

from app import service

SECRET = "unit-test-secret"


def _fields() -> dict:
    return {
        "certificate_number": "ZW-ENG-2025-0001",
        "holder_name": "Tendai Moyo",
        "qualification_name": "BSc Computer Science",
        "issuing_institution": "University of Zimbabwe",
        "date_issued": date(2024, 6, 30),
    }


def _sign(fields: dict, secret: str = SECRET) -> str:
    return service.compute_signature(
        fields["certificate_number"],
        fields["holder_name"],
        fields["qualification_name"],
        fields["issuing_institution"],
        fields["date_issued"],
        secret,
    )


def test_signature_is_deterministic():
    assert _sign(_fields()) == _sign(_fields())


def test_signature_changes_when_a_field_changes():
    base = _sign(_fields())
    tampered = _sign({**_fields(), "holder_name": "Someone Else"})
    assert base != tampered


def test_signature_depends_on_secret():
    assert _sign(_fields(), "secret-a") != _sign(_fields(), "secret-b")


def test_verify_integrity_accepts_untampered_record():
    fields = _fields()
    assert service.verify_integrity(fields, _sign(fields), SECRET) is True


def test_verify_integrity_detects_tampering():
    fields = _fields()
    signature = _sign(fields)
    fields["qualification_name"] = "PhD Computer Science"
    assert service.verify_integrity(fields, signature, SECRET) is False
