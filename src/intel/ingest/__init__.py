"""Snapshot build steps. Each step reads local inputs only and writes through one session."""

import csv
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

from sqlmodel import Session

from intel.enums import ClaimKind, Confidence, ProducedBy
from intel.models import Claim

# When the assignment materials were received; used as fetched_at for their sources so that
# rebuilds stay deterministic.
MATERIALS_RECEIVED_AT = datetime(2026, 10, 28, tzinfo=UTC)


@dataclass(frozen=True)
class Inputs:
    assignment_dir: Path = Path("docs/assignment")
    raw_dir: Path = Path("data/raw")
    manual_dir: Path = Path("data/manual")

    @property
    def mnc_workbook(self) -> Path:
        return self.assignment_dir / "10家大型药企创新药资产偏好分析.xlsx"

    @property
    def index_workbook(self) -> Path:
        return self.assignment_dir / "标普生物科技精选行业指数成分公司.xlsx"

    @property
    def sec_tickers(self) -> Path:
        return self.raw_dir / "sec" / "company_tickers.json"

    @property
    def link_results(self) -> Path:
        return self.raw_dir / "links" / "mnc_sources.json"

    @property
    def stage0_exclusions(self) -> Path:
        return self.manual_dir / "stage0_exclusions.csv"


@dataclass(frozen=True)
class Gap:
    entity: str
    key: str
    field: str
    reason: str
    location: str


GAP_COLUMNS = ("entity", "key", "field", "reason", "location")


@dataclass
class BuildContext:
    session: Session
    inputs: Inputs
    gaps: list[Gap] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def gap(self, entity: str, key: str, fld: str, reason: str, location: str) -> None:
        self.gaps.append(Gap(entity, key, fld, reason, location))

    def claim(
        self,
        entity: str,
        entity_id: int | str,
        fld: str,
        value: object,
        source_id: str,
        *,
        kind: ClaimKind = ClaimKind.fact,
        confidence: Confidence | None = None,
        produced_by: ProducedBy = ProducedBy.manual,
        as_of: date | None = None,
        note: str | None = None,
    ) -> None:
        self.session.add(
            Claim(
                entity_type=entity,
                entity_id=str(entity_id),
                field=fld,
                value=None if value is None else str(value),
                kind=kind,
                confidence=confidence,
                source_id=source_id,
                produced_by=produced_by,
                as_of=as_of,
                note=note,
            )
        )


def write_gaps(path: Path, gaps: list[Gap]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(GAP_COLUMNS)
        for g in sorted(gaps, key=lambda g: (g.entity, g.key, g.field, g.location)):
            writer.writerow([g.entity, g.key, g.field, g.reason, g.location])
