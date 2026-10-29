"""Analyst review files (data/manual/reviews/<TICKER>.toml) and the manual source register."""

import csv
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

from intel.enums import (
    Confidence,
    EventCertainty,
    EventImportance,
    ResearchStatus,
    RightsStatus,
    SourceType,
)
from intel.ingest import MATERIALS_RECEIVED_AT
from intel.models import Source
from intel.scoring import DIMENSIONS


class ReviewError(ValueError):
    """A review file that cannot be applied; the build stops so no half-reviewed data ships."""


@dataclass(frozen=True)
class Scored:
    score: int
    reason: str
    sources: list[str]
    confidence: Confidence = Confidence.medium


@dataclass(frozen=True)
class Cited:
    values: dict[str, str]
    sources: list[str]


@dataclass
class Review:
    ticker: str
    path: Path
    verified_by: str
    program: str
    indication: str | None
    buyer: str | None
    preference_rank: int | None
    status: ResearchStatus = ResearchStatus.reviewed
    deal_form: str | None = None
    need_item: str | None = None
    match_note: str | None = None
    thesis: str | None = None
    thesis_sources: list[str] = field(default_factory=list)
    scores: dict[str, Scored] = field(default_factory=dict)
    clinical: Cited | None = None
    event: Cited | None = None
    event_importance: EventImportance | None = None
    event_certainty: EventCertainty | None = None
    rights: RightsStatus | None = None
    rights_cited: Cited | None = None

    def all_sources(self) -> set[str]:
        ids = set(self.thesis_sources)
        ids.update(s for scored in self.scores.values() for s in scored.sources)
        for cited in (self.clinical, self.event, self.rights_cited):
            if cited:
                ids.update(cited.sources)
        return ids


def _cited(table: dict | None, keys: tuple[str, ...]) -> Cited | None:
    if not table:
        return None
    values = {k: str(table[k]).strip() for k in keys if str(table.get(k, "")).strip()}
    return Cited(values, list(table.get("sources", [])))


def parse(path: Path) -> Review | None:
    """The review, or None when nobody has signed it off yet."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    verified_by = str(data.get("verified_by", "")).strip()
    if not verified_by:
        return None
    try:
        scores = {}
        for dim, entry in data.get("scores", {}).items():
            if dim not in DIMENSIONS:
                raise ReviewError(f"{path.name}: unknown dimension {dim!r}")
            score = int(entry["score"])
            if not 0 <= score <= 4:
                raise ReviewError(f"{path.name}: {dim} score {score} outside 0–4")
            scores[dim] = Scored(
                score,
                entry["reason"],
                list(entry["sources"]),
                Confidence(entry.get("confidence", Confidence.medium)),
            )
        event = data.get("event") or {}
        rights = data.get("rights") or {}
        thesis = data.get("thesis") or []
        return Review(
            ticker=path.stem.upper(),
            path=path,
            verified_by=verified_by,
            program=data["program"],
            indication=data.get("indication"),
            buyer=data.get("buyer"),
            preference_rank=data.get("preference_rank"),
            status=ResearchStatus(data.get("status", ResearchStatus.reviewed)),
            deal_form=data.get("deal_form"),
            need_item=data.get("need_item"),
            match_note=data.get("match_note"),
            thesis="".join(thesis) if isinstance(thesis, list) else thesis,
            thesis_sources=list(data.get("thesis_sources", [])),
            scores=scores,
            clinical=_cited(
                data.get("clinical"), ("design", "comparability", "result", "limitation")
            ),
            event=_cited(event, ("text", "timing")),
            event_importance=EventImportance(event["importance"])
            if "importance" in event
            else None,
            event_certainty=EventCertainty(event["certainty"]) if "certainty" in event else None,
            rights=RightsStatus(rights["status"]) if rights.get("status") else None,
            rights_cited=_cited(rights, ("note",)),
        )
    except (KeyError, ValueError) as exc:
        if isinstance(exc, ReviewError):
            raise
        raise ReviewError(f"{path.name}: {exc!r}") from exc


def load_reviews(reviews_dir: Path) -> dict[str, Review]:
    if not reviews_dir.exists():
        return {}
    reviews = (parse(p) for p in sorted(reviews_dir.glob("*.toml")))
    return {r.ticker: r for r in reviews if r}


SOURCE_COLUMNS = (
    "source_id",
    "url",
    "source_type",
    "title",
    "publisher",
    "published_date",
    "accessed_on",
    "note",
)


def load_manual_sources(path: Path) -> list[Source]:
    if not path.exists():
        return []
    sources = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if not row["source_id"].strip().startswith("MAN-"):
                raise ReviewError(f"sources.csv: id {row['source_id']!r} must start with MAN-")
            published = row["published_date"].strip()
            accessed = row["accessed_on"].strip()
            sources.append(
                Source(
                    source_id=row["source_id"].strip(),
                    url=row["url"].strip() or None,
                    source_type=SourceType(row["source_type"].strip()),
                    title=row["title"].strip() or None,
                    publisher=row["publisher"].strip() or None,
                    note=row["note"].strip() or None,
                    published_date_text=published or None,
                    published_date=_full_date(published),
                    fetched_at=(
                        datetime.fromisoformat(accessed).replace(tzinfo=UTC)
                        if accessed
                        else MATERIALS_RECEIVED_AT
                    ),
                )
            )
    return sources


def _full_date(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None
