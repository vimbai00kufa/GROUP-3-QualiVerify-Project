"""HTTP API for the Qualification Verification System."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import service
from .database import make_session_factory
from .models import AuditLog, Qualification
from .roles import Role, current_actor, require_any_role, require_role
from .schemas import QualificationCreate, VerifyRequest

router = APIRouter()

session_factory = make_session_factory()

STATUS_ACTIVE = "ACTIVE"
STATUS_REVOKED = "REVOKED"

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


def get_db(request: Request) -> Session:
    """Yield a database session bound to the app's engine."""
    session = session_factory(bind=request.app.state.engine)
    try:
        yield session
    finally:
        session.close()


def _log(db: Session, action: str, actor: str, detail: str = "") -> None:
    """Append an immutable entry to the audit trail (R4)."""
    db.add(AuditLog(action=action, actor=actor, detail=detail))
    db.commit()


# ---------------------------------------------------------------------------
# R1 - Register qualifications (admin only)
# ---------------------------------------------------------------------------


@router.post("/qualifications", status_code=201, tags=["register"])
def register_qualification(
    payload: QualificationCreate,
    request: Request,
    db: Session = Depends(get_db),
    role: str = Depends(require_role(Role.ADMINISTRATOR, Role.REGISTRAR)),
    actor: str = Depends(current_actor),
):
    """Register a new qualification record and sign it (R1).

    RBAC: Administrator and Registrar only -- an institution/registrar is the
    party that actually issues qualifications, so it is granted the same
    registration right as an Administrator (see docs/RBAC.md matrix).
    """
    existing = db.scalar(
        select(Qualification).where(Qualification.certificate_number == payload.certificate_number)
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Certificate {payload.certificate_number} is already registered",
        )

    settings = request.app.state.settings
    record = Qualification(
        certificate_number=payload.certificate_number,
        holder_name=payload.holder_name.strip(),
        qualification_name=payload.qualification_name.strip(),
        issuing_institution=payload.issuing_institution.strip(),
        date_issued=payload.date_issued,
        signature=service.compute_signature(
            payload.certificate_number,
            payload.holder_name.strip(),
            payload.qualification_name.strip(),
            payload.issuing_institution.strip(),
            payload.date_issued,
            settings.hmac_secret_key,
        ),
        status=STATUS_ACTIVE,
        registered_by=actor,
    )
    db.add(record)
    db.commit()
    _log(db, "REGISTRATION", actor, f"Registered certificate {record.certificate_number}")
    return {
        "id": record.id,
        "certificate_number": record.certificate_number,
        "holder_name": record.holder_name,
        "qualification_name": record.qualification_name,
        "issuing_institution": record.issuing_institution,
        "date_issued": record.date_issued.isoformat(),
        "status": record.status,
    }


# ---------------------------------------------------------------------------
# R2 - Search and retrieve records (verifier / admin)
# ---------------------------------------------------------------------------


@router.get("/qualifications", tags=["search"])
def search_qualifications(
    query: str = Query(min_length=2, max_length=120),
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role()),
    actor: str = Depends(current_actor),
):
    """Search records by holder name or certificate number (R2).

    RBAC: open to all four authenticated roles -- every role is permitted to
    view/search permitted records per the assignment's permission matrix.
    """
    like = f"%{query.strip()}%"
    records = db.scalars(
        select(Qualification)
        .where(
            (Qualification.holder_name.ilike(like)) | (Qualification.certificate_number.ilike(like))
        )
        .limit(20)
    ).all()
    _log(db, "SEARCH", actor, f"Search query: {query.strip()}")
    return [
        {
            "id": r.id,
            "certificate_number": r.certificate_number,
            "holder_name": r.holder_name,
            "qualification_name": r.qualification_name,
            "issuing_institution": r.issuing_institution,
            "date_issued": r.date_issued.isoformat(),
            "status": r.status,
        }
        for r in records
    ]


# ---------------------------------------------------------------------------
# R3 - Verify authenticity (public)
# ---------------------------------------------------------------------------


@router.post("/verify", tags=["verify"])
def verify_qualification(
    payload: VerifyRequest,
    request: Request,
    db: Session = Depends(get_db),
    actor: str = Depends(current_actor),
):
    """Verify a qualification: record exists + name matches + integrity OK (R3).

    RBAC: deliberately left public/unauthenticated -- verification is the
    system's public-facing purpose (anyone holding a certificate number and
    name should be able to check it), so it is outside the role matrix by
    design. This matches the assignment's Standard User capability to
    "submit or request verification" without any extra role check. See
    docs/RBAC.md for the full justification.
    """
    record = db.scalar(
        select(Qualification).where(Qualification.certificate_number == payload.certificate_number)
    )

    def invalid(reason: str, log_detail: str) -> dict:
        _log(db, "VERIFY_FAILED", actor, log_detail)
        return {
            "certificate_number": payload.certificate_number,
            "result": "INVALID",
            "reason": reason,
        }

    if record is None:
        return invalid("No qualification found for this certificate number", "No record found")

    if record.holder_name.lower() != payload.holder_name.strip().lower():
        return invalid("Holder name does not match the registered record", "Holder name mismatch")

    settings = request.app.state.settings
    fields = {
        "certificate_number": record.certificate_number,
        "holder_name": record.holder_name,
        "qualification_name": record.qualification_name,
        "issuing_institution": record.issuing_institution,
        "date_issued": record.date_issued,
    }
    if not service.verify_integrity(fields, record.signature, settings.hmac_secret_key):
        return invalid(
            "Integrity check failed: record may have been tampered with",
            "Integrity check failed",
        )

    if record.status == STATUS_REVOKED:
        return invalid("Qualification has been revoked", "Revoked qualification verified")

    _log(db, "VERIFY_SUCCESS", actor, f"Verified certificate {record.certificate_number}")
    return {
        "certificate_number": record.certificate_number,
        "result": "VALID",
        "reason": None,
        "holder_name": record.holder_name,
        "qualification_name": record.qualification_name,
        "issuing_institution": record.issuing_institution,
        "date_issued": record.date_issued.isoformat(),
        "status": record.status,
    }


# ---------------------------------------------------------------------------
# Revocation (admin)
# ---------------------------------------------------------------------------


@router.post("/qualifications/{record_id}/revoke", tags=["register"])
def revoke_qualification(
    record_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_role(Role.ADMINISTRATOR)),
    actor: str = Depends(current_actor),
):
    """Mark a qualification as revoked so future verifications fail.

    RBAC: Administrator only -- revocation is a higher-impact action than
    registration, so it is deliberately kept narrower than the Registrar's
    registration right (see docs/RBAC.md).
    """
    record = db.get(Qualification, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Qualification not found")
    record.status = STATUS_REVOKED
    db.commit()
    _log(db, "REVOCATION", actor, f"Revoked certificate {record.certificate_number}")
    return {
        "id": record.id,
        "certificate_number": record.certificate_number,
        "status": record.status,
    }


# ---------------------------------------------------------------------------
# R4 - Auditable history (admin)
# ---------------------------------------------------------------------------


@router.get("/audit", tags=["audit"])
def list_audit_log(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    role: str = Depends(require_role(Role.ADMINISTRATOR, Role.VERIFICATION_OFFICER)),
):
    """Return the audit trail, newest first (R4).

    RBAC: Administrator and Verification Officer -- the officer needs the
    trail to review prior verification decisions; Registrar and Standard
    User are denied (see docs/RBAC.md permission matrix and assumptions).
    """
    rows = db.scalars(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(limit).offset(offset)
    ).all()
    return [
        {
            "id": row.id,
            "timestamp": row.timestamp.isoformat(),
            "action": row.action,
            "actor": row.actor,
            "detail": row.detail,
        }
        for row in rows
    ]
