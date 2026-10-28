"""Read-only HTTP API over the snapshot; also serves the built frontend."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session

from intel.config import load_settings
from intel.db import entity_counts, ro_engine
from intel.models import SnapshotMeta


class Health(BaseModel):
    status: str


class Meta(BaseModel):
    generated_at: datetime | None
    generator: str | None
    counts: dict[str, int]


def create_app(db_path: Path | None = None, web_dist: Path | None = None) -> FastAPI:
    settings = load_settings()
    engine = ro_engine(db_path or settings.db_path)
    web_dist = web_dist or settings.web_dist

    def get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI(title="Drug Asset Intel", version="0.1.0")

    @app.get("/api/health", response_model=Health)
    def health() -> Health:
        return Health(status="ok")

    @app.get("/api/meta", response_model=Meta)
    def meta(session: Annotated[Session, Depends(get_session)]) -> Meta:
        row = session.get(SnapshotMeta, 1)
        return Meta(
            # SQLite drops tzinfo; snapshot times are always written in UTC.
            generated_at=row.generated_at.replace(tzinfo=UTC) if row else None,
            generator=row.generator if row else None,
            counts=entity_counts(session),
        )

    if web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
    return app
