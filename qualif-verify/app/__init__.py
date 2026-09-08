"""Application factory for the Qualification Verification System (QVS)."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import Settings, get_settings
from .database import Base, make_engine
from .routes import router

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = settings or get_settings()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="DevOps-enabled qualification verification system (MIM736).",
    )
    app.state.settings = settings
    app.state.engine = engine
    app.include_router(router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness probe used by Docker and monitoring."""
        return {"status": "ok"}

    # Web UI (mounted last so the API routes and /docs take priority).
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app
