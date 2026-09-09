"""Application configuration (environment driven)."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Runtime settings. All values can be overridden via environment variables."""

    database_url: str
    hmac_secret_key: str
    app_name: str = "Qualification Verification System"
    app_version: str = "1.0.0"


def get_settings() -> Settings:
    """Build settings from the environment (with development defaults)."""
    return Settings(
        database_url=os.environ.get("QVS_DATABASE_URL", "sqlite:///./qvs.db"),
        hmac_secret_key=os.environ.get("QVS_HMAC_SECRET", "dev-only-change-me"),
    )
