from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.database import engine
from app.routers import sightings


def create_app() -> FastAPI:
    app = FastAPI(title="WildTrace API", version="0.1.0")

    app.include_router(
        sightings.router,
        prefix="/api/v1",
        tags=["sightings"]
    )

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "ready"}
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="not ready"
            )

    return app

app = create_app()