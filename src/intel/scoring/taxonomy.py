"""Therapeutic areas: tag derived indications and map buyer preferences, from manual files."""

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from sqlmodel import select

from intel.enums import ClaimKind, Confidence, PreferenceDimension, ProducedBy, Stage
from intel.ingest import BuildContext
from intel.models import Buyer, BuyerPreference, Claim, ProgramIndication

SKIP = "skip"  # keyword class for registry entries that are not diseases (PK, healthy volunteers)


@dataclass(frozen=True)
class PreferenceMap:
    ta_codes: frozenset[str]
    stage_min: Stage
    stage_max: Stage


def load_keywords(path: Path) -> list[tuple[str, re.Pattern[str]]]:
    with path.open(encoding="utf-8") as fh:
        return [
            (row["ta"], re.compile(r"\b" + re.escape(row["keyword"].strip().lower())))
            for row in csv.DictReader(fh)
            if row["keyword"].strip()
        ]


def classify(text: str | None, keywords) -> tuple[list[str], list[str]]:
    """Areas the text falls in, and the keywords that hit; a `skip` hit means no area."""
    if not text:
        return [], []
    low = text.lower()
    hits: dict[str, list[str]] = defaultdict(list)
    for ta, pattern in keywords:
        if pattern.search(low):
            hits[ta].append(pattern.pattern.removeprefix(r"\b").replace("\\", ""))
    if SKIP in hits:
        return [], hits[SKIP]
    return sorted(hits), [k for ta in sorted(hits) for k in hits[ta]]


def load_preference_map(path: Path) -> dict[tuple[str, int], PreferenceMap]:
    """Only rows a person has verified take effect."""
    with path.open(encoding="utf-8") as fh:
        return {
            (row["buyer"], int(row["rank"])): PreferenceMap(
                frozenset(c for c in row["ta_codes"].split(";") if c),
                Stage(row["stage_min"]),
                Stage(row["stage_max"]),
            )
            for row in csv.DictReader(fh)
            if row["verified_by"].strip()
        }


def mapped_preferences(ctx: BuildContext) -> list[tuple[BuyerPreference, PreferenceMap]]:
    if not ctx.inputs.buyer_preference_map.exists():
        return []
    mapping = load_preference_map(ctx.inputs.buyer_preference_map)
    rows = ctx.session.exec(
        select(BuyerPreference, Buyer)
        .join(Buyer)
        .where(BuyerPreference.dimension == PreferenceDimension.therapeutic_area)
    ).all()
    return [(p, mapping[(b.name, p.rank)]) for p, b in rows if (b.name, p.rank) in mapping]


def ingest(ctx: BuildContext) -> None:
    if not ctx.inputs.ta_keywords.exists():
        ctx.notes.append("ta_keywords.csv missing: therapeutic areas left empty")
        return
    keywords = load_keywords(ctx.inputs.ta_keywords)
    indication_sources: dict[str, list[str]] = defaultdict(list)
    for entity_id, source_id in ctx.session.exec(
        select(Claim.entity_id, Claim.source_id).where(
            Claim.entity_type == "program_indication", Claim.field == "indication"
        )
    ):
        indication_sources[entity_id].append(source_id)
    for pi in ctx.session.exec(select(ProgramIndication)).all():
        areas, hits = classify(pi.indication, keywords)
        if not areas:
            continue
        pi.therapeutic_area = ";".join(areas)
        for source_id in indication_sources[str(pi.id)]:
            ctx.claim(
                "program_indication",
                pi.id,
                "therapeutic_area",
                pi.therapeutic_area,
                source_id,
                kind=ClaimKind.inference,
                confidence=Confidence.medium,
                produced_by=ProducedBy.manual,
                note=f"按 data/manual/ta_keywords.csv 关键词归类；命中：{', '.join(hits)}",
            )
