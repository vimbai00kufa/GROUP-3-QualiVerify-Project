"""Pydantic schemas: the declarative validation rules of the API."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class QualificationCreate(BaseModel):
    """Validation rules applied when registering a qualification (R1)."""

    certificate_number: str = Field(
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9-]+$",
        description="Unique certificate reference, e.g. ZW-ENG-2025-0001",
    )
    holder_name: str = Field(
        min_length=3,
        max_length=120,
        pattern=r"^[A-Za-z][A-Za-z' .-]*$",
        description="Full name of the qualification holder (letters, spaces, ' . -)",
    )
    qualification_name: str = Field(min_length=3, max_length=200)
    issuing_institution: str = Field(min_length=3, max_length=150)
    date_issued: date

    @field_validator("certificate_number")
    @classmethod
    def normalise_certificate(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("date_issued")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date_issued cannot be in the future")
        return value


class VerifyRequest(BaseModel):
    """Validation rules applied when verifying a qualification (R3)."""

    certificate_number: str = Field(min_length=8, max_length=64)
    holder_name: str = Field(min_length=3, max_length=120)

    @field_validator("certificate_number")
    @classmethod
    def normalise_certificate(cls, value: str) -> str:
        return value.strip().upper()
