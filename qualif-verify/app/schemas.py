"""QVS - Schemas (skeleton, simple texts only, no logic)."""

from pydantic import BaseModel


class QualificationPlaceholder(BaseModel):
    """Skeleton placeholder schema."""

    message: str = "Qualification schema placeholder"


class VerifyPlaceholder(BaseModel):
    """Skeleton placeholder schema."""

    message: str = "Verify schema placeholder"
