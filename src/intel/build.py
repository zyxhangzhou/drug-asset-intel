"""Rebuild the snapshot from local inputs only: materials, raw caches and manual files."""

import os
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from sqlmodel import Session

from intel.db import init_db, touch_snapshot
from intel.ingest import BuildContext, Gap, Inputs, write_gaps

Step = Callable[[BuildContext], None]


def default_steps() -> list[Step]:
    from intel.ingest import mnc, universe

    return [mnc.ingest, universe.ingest]


@dataclass
class BuildReport:
    gaps: list[Gap]
    notes: list[str]

    def gap_summary(self) -> Counter[str]:
        return Counter(g.reason for g in self.gaps)


def build_snapshot(
    db_path: Path,
    inputs: Inputs | None = None,
    steps: Sequence[Step] | None = None,
    gaps_path: Path | None = None,
) -> BuildReport:
    """Build into a temp file and swap it in; the old snapshot survives any failure."""
    inputs = inputs or Inputs()
    steps = default_steps() if steps is None else steps
    tmp = db_path.with_name(db_path.name + ".tmp")
    tmp.unlink(missing_ok=True)
    try:
        engine = init_db(tmp)
        with Session(engine) as session:
            ctx = BuildContext(session=session, inputs=inputs)
            for step in steps:
                step(ctx)
                session.flush()
            touch_snapshot(session)
            session.commit()
        engine.dispose()
        os.replace(tmp, db_path)
    finally:
        tmp.unlink(missing_ok=True)
    write_gaps(gaps_path or db_path.with_name("gaps.csv"), ctx.gaps)
    return BuildReport(gaps=ctx.gaps, notes=ctx.notes)
