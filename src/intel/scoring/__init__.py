"""Pure scoring rules from docs/scoring-rules.md, shared by the build and the API."""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from intel.enums import EventCertainty, EventImportance, RightsStatus, Stage

DIMENSIONS = ("buyer_fit", "stage_match", "clinical", "catalyst", "dealability")
DEFAULT_CONFIG = Path("config/scoring.toml")

# Auto screening uses structured data only, so these dimensions cannot exceed tag-level scores.
AUTO_CAPS = {"buyer_fit": 2, "clinical": 2}

# Ordinal position of each stage; phase 2a / 2b are not distinguished by the registry.
STAGE_ORDER = {
    Stage.preclinical: 0.0,
    Stage.phase1: 1.0,
    Stage.phase1_2: 1.5,
    Stage.phase2: 2.0,
    Stage.phase2_3: 2.5,
    Stage.phase3: 3.0,
    Stage.filed: 4.0,
    Stage.approved: 5.0,
}

CATALYST_SCORES = {
    (EventImportance.high, EventCertainty.disclosed): 4,
    (EventImportance.high, EventCertainty.estimated): 3,
    (EventImportance.medium, EventCertainty.disclosed): 3,
    (EventImportance.medium, EventCertainty.estimated): 2,
    (EventImportance.low, EventCertainty.disclosed): 1,
    (EventImportance.low, EventCertainty.estimated): 1,
}

RIGHTS_CAPS = {RightsStatus.full: 4, RightsStatus.partial: 3, RightsStatus.restricted: 1}


@dataclass(frozen=True)
class ScoringConfig:
    weights: dict[str, float]
    ev_tiers: list[tuple[float, int]]
    catalyst_window_months: int
    longlist_size: int
    shortlist_max: int
    funding_pressure_months: float

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG) -> "ScoringConfig":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        s = data["screening"]
        return cls(
            weights=normalize_weights(data["weights"]),
            ev_tiers=sorted((t["below"], t["score"]) for t in data["ev_tiers"]),
            catalyst_window_months=s["catalyst_window_months"],
            longlist_size=s["longlist_size"],
            shortlist_max=s["shortlist_max"],
            funding_pressure_months=s["funding_pressure_months"],
        )


def normalize_weights(raw: Mapping[str, float]) -> dict[str, float]:
    if set(raw) != set(DIMENSIONS):
        raise ValueError(f"weights must name exactly {DIMENSIONS}, got {sorted(raw)}")
    if any(w < 0 for w in raw.values()):
        raise ValueError("weights must be non-negative")
    total = sum(raw.values())
    if total == 0:
        raise ValueError("at least one weight must be positive")
    return {d: raw[d] / total for d in DIMENSIONS}


def total(scores: Mapping[str, int | None], weights: Mapping[str, float], missing: int) -> float:
    """Weighted score on 0–100; `missing` is what an empty dimension counts as (0 or 4)."""
    value = sum(weights[d] * (missing if scores.get(d) is None else scores[d]) for d in DIMENSIONS)
    return round(value / 4 * 100, 1)


def conservative(scores: Mapping[str, int | None], weights: Mapping[str, float]) -> float:
    return total(scores, weights, missing=0)


def optimistic(scores: Mapping[str, int | None], weights: Mapping[str, float]) -> float:
    return total(scores, weights, missing=4)


def stage_match(stage: Stage, lo: Stage, hi: Stage) -> int | None:
    if stage not in STAGE_ORDER:
        return None
    pos, low, high = STAGE_ORDER[stage], STAGE_ORDER[lo], STAGE_ORDER[hi]
    distance = max(low - pos, pos - high, 0.0)
    if distance == 0:
        return 4
    return 2 if distance <= 1 else 0


def ev_score(ev: float, tiers: list[tuple[float, int]]) -> int:
    for below, score in tiers:
        if ev < below:
            return score
    return 0


def dealability(ev: float | None, rights: RightsStatus | None, tiers) -> int | None:
    if ev is None:
        return None
    score = ev_score(ev, tiers)
    return min(score, RIGHTS_CAPS[rights]) if rights else score


def catalyst_score(importance: EventImportance | None, certainty: EventCertainty | None) -> int:
    if importance is None or certainty is None:
        return 0
    return CATALYST_SCORES[(importance, certainty)]
