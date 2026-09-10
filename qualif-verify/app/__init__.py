"""QVS - App factory (skeleton, no logic)."""

from fastapi import FastAPI

from app.routes import router


def create_app() -> FastAPI:
    """Create and return the FastAPI app."""
    app = FastAPI(
        title="Qualification Verification System (QVS)",
        description="MIM736 Practical Assignment - skeleton only",
        version="0.1.0",
    )

    app.include_router(router)

    @app.get("/", tags=["root"])
    def root():
        return {"message": "QVS API - skeleton running"}

    @app.get("/health", tags=["root"])
    def health():
        return {"message": "OK - skeleton health check"}

    return app
