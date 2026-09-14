"""Unit tests for input validation rules (R1 validation)."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas import QualificationCreate


def _valid_payload() -> dict:
    return {
        "certificate_number": "ZW-ENG-2025-0001",
        "holder_name": "Tendai Moyo",
        "qualification_name": "BSc Computer Science",
        "issuing_institution": "University of Zimbabwe",
        "date_issued": "2024-06-30",
    }


def test_valid_payload_is_accepted():
    QualificationCreate(**_valid_payload())


def test_certificate_too_short_is_rejected():
    payload = _valid_payload()
    payload["certificate_number"] = "ABC"
    with pytest.raises(ValidationError):
        QualificationCreate(**payload)


def test_certificate_with_spaces_is_rejected():
    payload = _valid_payload()
    payload["certificate_number"] = "BAD CERT 1"
    with pytest.raises(ValidationError):
        QualificationCreate(**payload)


def test_holder_name_with_digits_is_rejected():
    payload = _valid_payload()
    payload["holder_name"] = "John123"
    with pytest.raises(ValidationError):
        QualificationCreate(**payload)


def test_future_issue_date_is_rejected():
    payload = _valid_payload()
    payload["date_issued"] = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError):
        QualificationCreate(**payload)


def test_certificate_number_is_normalised_to_uppercase():
    payload = _valid_payload()
    payload["certificate_number"] = "zw-eng-2025-0001"
    assert QualificationCreate(**payload).certificate_number == "ZW-ENG-2025-0001"
