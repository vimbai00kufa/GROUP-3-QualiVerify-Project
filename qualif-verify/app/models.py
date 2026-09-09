"""ORM models: qualifications and the audit trail."""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    """Timezone-aware UTC timestamp (Python 3.12+ deprecates utcnow)."""
    return datetime.now(timezone.utc)


class Qualification(Base):
    """A registered qualification / certification record."""

    __tablename__ = "qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    certificate_number: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    holder_name: Mapped[str] = mapped_column(String(120), nullable=False)
    qualification_name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuing_institution: Mapped[str] = mapped_column(String(150), nullable=False)
    date_issued: Mapped[date] = mapped_column(Date, nullable=False)
    signature: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    registered_by: Mapped[str] = mapped_column(String(80), nullable=False)

    def __repr__(self) -> str:
        return f"<Qualification {self.certificate_number} {self.holder_name}>"


class AuditLog(Base):
    """Append-only audit trail of all verification-related activity (R4).

    Deliberately has no update/delete API: history is immutable.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, index=True
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
