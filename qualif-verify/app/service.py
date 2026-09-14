"""Core verification logic, decoupled from the HTTP layer (unit-testable)."""

import hashlib
import hmac
from datetime import date


def compute_signature(
    certificate_number: str,
    holder_name: str,
    qualification_name: str,
    issuing_institution: str,
    date_issued: date,
    secret: str,
) -> str:
    """Return the HMAC-SHA256 integrity signature for a record.

    The signature binds every field of the record to the issuing secret,
    so any tampering with the stored data invalidates the verification.
    """
    canonical = "|".join(
        [
            certificate_number.strip().upper(),
            holder_name.strip(),
            qualification_name.strip(),
            issuing_institution.strip(),
            date_issued.isoformat(),
        ]
    )
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_integrity(record_fields: dict, stored_signature: str, secret: str) -> bool:
    """Re-compute the signature for the given fields and compare with the stored one."""
    expected = compute_signature(
        record_fields["certificate_number"],
        record_fields["holder_name"],
        record_fields["qualification_name"],
        record_fields["issuing_institution"],
        record_fields["date_issued"],
        secret,
    )
    return hmac.compare_digest(expected, stored_signature)
