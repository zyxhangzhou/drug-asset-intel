"""Read-only HTTP API over the snapshot; also serves the built frontend."""

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session

from intel.config import load_settings
from intel.db import entity_counts, ro_engine
from intel.models import SnapshotMeta
from intel.scoring import DIMENSIONS, ScoringConfig, checks, normalize_weights


class Health(BaseModel):
    status: str


class Meta(BaseModel):
    generated_at: datetime | None
    generator: str | None
    snapshot_date: date | None
    counts: dict[str, int]


class ShortlistItem(BaseModel):
    rank: int
    ticker: str
    name: str
    asset: str | None
    indication: str | None
    stage: str | None
    buyer: str | None
    preference: str | None
    scores: dict[str, int | None]
    conservative: float
    optimistic: float
    coverage: float
    research_status: str
    shortlisted: bool
    next_event: str | None
    event_timing: str | None
    enterprise_value: float | None
    rights_status: str | None
    funding_flag: str | None
    thesis: str | None


class Shortlist(BaseModel):
    weights: dict[str, float]
    items: list[ShortlistItem]


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
            snapshot_date=row.snapshot_date if row else None,
            counts=entity_counts(session),
        )

    @app.get("/api/shortlist", response_model=Shortlist)
    def shortlist(
        session: Annotated[Session, Depends(get_session)],
        weights: Annotated[
            str | None, Query(description="Five comma-separated weights: " + ",".join(DIMENSIONS))
        ] = None,
    ) -> Shortlist:
        if weights is None:
            w = ScoringConfig.load().weights
        else:
            try:
                values = [float(x) for x in weights.split(",")]
                w = normalize_weights(dict(zip(DIMENSIONS, values, strict=True)))
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        items = []
        for i, r in enumerate(checks.rank(checks.primaries(session), w), 1):
            rec, pi, pref = r.rec, r.rec.indication, r.rec.preference
            items.append(
                ShortlistItem(
                    rank=i,
                    ticker=rec.target.ticker,
                    name=rec.target.name,
                    asset=pi.program.name if pi else None,
                    indication=pi.indication if pi else None,
                    stage=pi.stage if pi else None,
                    buyer=pref.buyer.name if pref else None,
                    preference=pref.label if pref else None,
                    scores={d: getattr(rec, d) for d in DIMENSIONS},
                    conservative=r.conservative,
                    optimistic=r.optimistic,
                    coverage=rec.coverage,
                    research_status=rec.research_status,
                    shortlisted=rec.target.shortlisted,
                    next_event=rec.next_event,
                    event_timing=rec.event_timing,
                    enterprise_value=rec.enterprise_value,
                    rights_status=rec.rights_status,
                    funding_flag=rec.funding_flag,
                    thesis=rec.thesis,
                )
            )
        return Shortlist(weights=w, items=items)

    if web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="web")
    return app
