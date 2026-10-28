"""Engines, write-time integrity rules, and snapshot helpers."""

import hashlib
import typing
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path

from sqlalchemy import Engine, event, func
from sqlmodel import Session, SQLModel, create_engine, select

from intel.enums import ClaimKind, ProducedBy, SourceType
from intel.models import DOMAIN_TABLES, Claim, SnapshotMeta, Source

GENERATOR = "intel 0.1.0"


class IntegrityViolation(ValueError):
    """A write that breaks a provenance or vocabulary rule."""


def _enable_foreign_keys(dbapi_conn, _record) -> None:
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


def rw_engine(path: Path) -> Engine:
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    event.listen(engine, "connect", _enable_foreign_keys)
    return engine


def ro_engine(path: Path) -> Engine:
    if not path.exists():
        raise FileNotFoundError(f"snapshot not found: {path.resolve()}")
    engine = create_engine(
        f"sqlite:///file:{path.resolve()}?mode=ro&uri=true",
        connect_args={"check_same_thread": False},
    )
    event.listen(engine, "connect", _enable_foreign_keys)
    return engine


def init_db(path: Path) -> Engine:
    """Create all tables; safe to re-run on an existing snapshot."""
    engine = rw_engine(path)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.get(SnapshotMeta, 1) is None:
            session.add(SnapshotMeta(generated_at=datetime.now(UTC), generator=GENERATOR))
            session.commit()
    return engine


def touch_snapshot(session: Session) -> None:
    """Record that the snapshot content was (re)generated now."""
    meta = session.get(SnapshotMeta, 1)
    if meta is None:
        meta = SnapshotMeta(generated_at=datetime.now(UTC), generator=GENERATOR)
    meta.generated_at = datetime.now(UTC)
    meta.generator = GENERATOR
    session.add(meta)


# --- write-time rules -------------------------------------------------------------------


def _enum_fields(model: type[SQLModel]) -> dict[str, type[Enum]]:
    out = {}
    for name, info in model.model_fields.items():
        for candidate in (info.annotation, *typing.get_args(info.annotation)):
            if isinstance(candidate, type) and issubclass(candidate, Enum):
                out[name] = candidate
    return out


def _check_vocabulary(obj: SQLModel) -> None:
    for name, enum_cls in _enum_fields(type(obj)).items():
        value = getattr(obj, name)
        if value is None or isinstance(value, enum_cls):
            continue
        allowed = [m.value for m in enum_cls]
        if value not in allowed:
            raise IntegrityViolation(
                f"{type(obj).__name__}.{name}={value!r} is not allowed; use one of {allowed}"
            )


def _check_claim(session: Session, claim: Claim) -> None:
    with session.no_autoflush:
        registered = session.get(Source, claim.source_id) is not None or any(
            isinstance(o, Source) and o.source_id == claim.source_id for o in session.new
        )
    if not registered:
        raise IntegrityViolation(f"claim references unregistered source {claim.source_id!r}")
    if claim.kind == ClaimKind.inference and claim.confidence is None:
        raise IntegrityViolation("inference claims must carry a confidence")
    if claim.produced_by == ProducedBy.llm and not (claim.quote and claim.quote.strip()):
        raise IntegrityViolation("llm claims must carry a verbatim quote")
    if claim.produced_by == ProducedBy.llm and not claim.model:
        raise IntegrityViolation("llm claims must name the model that produced them")


@event.listens_for(Session, "before_flush")
def _enforce_rules(session: Session, _ctx, _instances) -> None:
    for obj in [*session.new, *session.dirty]:
        if isinstance(obj, SQLModel):
            _check_vocabulary(obj)
        if isinstance(obj, Claim):
            _check_claim(session, obj)


# --- sources --------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archived_source(
    source_id: str,
    source_type: SourceType,
    local_path: Path,
    *,
    url: str | None = None,
    title: str | None = None,
    published_date: date | None = None,
    fetched_at: datetime | None = None,
) -> Source:
    """Build a Source for a document saved on disk, recording its content hash."""
    return Source(
        source_id=source_id,
        source_type=source_type,
        url=url,
        title=title,
        published_date=published_date,
        fetched_at=fetched_at or datetime.now(UTC),
        local_path=str(local_path),
        content_hash=sha256_file(local_path),
    )


def archive_matches(source: Source) -> bool:
    return bool(source.local_path) and sha256_file(Path(source.local_path)) == source.content_hash


# --- provenance -----------------------------------------------------------------------


def _has_value(value: object) -> bool:
    return value is not None and not (isinstance(value, str) and not value.strip())


def provenance_gaps(session: Session) -> list[tuple[str, str, str]]:
    """(entity_type, entity_id, field) for every non-empty business field without a claim."""
    claimed = set(session.exec(select(Claim.entity_type, Claim.entity_id, Claim.field)).all())
    gaps = []
    for model in DOMAIN_TABLES:
        table = model.__tablename__
        for row in session.exec(select(model)).all():
            for name in model.BUSINESS_FIELDS:
                key = (table, str(row.id), name)
                if _has_value(getattr(row, name)) and key not in claimed:
                    gaps.append(key)
    return gaps


def entity_counts(session: Session) -> dict[str, int]:
    return {
        model.__tablename__: session.exec(select(func.count()).select_from(model)).one()
        for model in DOMAIN_TABLES
    }
