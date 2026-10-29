"""Reads over a built snapshot: reweighted ranking and the sample checks of scoring-rules §6."""

from dataclasses import dataclass

from sqlmodel import Session, select

from intel import scoring
from intel.enums import ResearchStatus
from intel.models import Claim, Recommendation

# A 3–4 score must rest on the fact it summarizes: (field on the pair, or the indication stage).
EVIDENCE = {
    "buyer_fit": "need_item",
    "stage_match": "stage",
    "clinical": "result",
    "catalyst": "event_timing",
    "dealability": "enterprise_value",
}


@dataclass(frozen=True)
class Ranked:
    rec: Recommendation
    conservative: float
    optimistic: float


def primaries(session: Session) -> list[Recommendation]:
    return list(session.exec(select(Recommendation).where(Recommendation.is_primary)).all())


def rank(recs: list[Recommendation], weights: dict[str, float]) -> list[Ranked]:
    rows = []
    for rec in recs:
        scores = {d: getattr(rec, d) for d in scoring.DIMENSIONS}
        rows.append(
            Ranked(rec, scoring.conservative(scores, weights), scoring.optimistic(scores, weights))
        )
    return sorted(rows, key=lambda r: (-r.conservative, -r.optimistic, r.rec.target.ticker))


def unsupported_high_scores(session: Session, recs: list[Recommendation]) -> list[str]:
    claimed = set(session.exec(select(Claim.entity_type, Claim.entity_id, Claim.field)).all())
    problems = []
    for rec in recs:
        for dim, evidence in EVIDENCE.items():
            if (getattr(rec, dim) or 0) < 3:
                continue
            if evidence == "stage":
                ok = rec.program_indication_id is not None and (
                    ("program_indication", str(rec.program_indication_id), "stage") in claimed
                )
            else:
                ok = ("recommendation", str(rec.id), evidence) in claimed
            if not ok:
                problems.append(f"{rec.target.ticker}: {dim}={getattr(rec, dim)} lacks {evidence}")
    return problems


def coverage_bias(ranked: list[Ranked], top: int = 10, floor: float = 0.7) -> list[str]:
    """Among reviewed companies (the only ones that can be recommended), the top must be well
    covered; auto-screened companies are not yet candidates for recommendation."""
    reviewed = [r for r in ranked if r.rec.research_status != ResearchStatus.auto][:top]
    return [
        f"{r.rec.target.ticker}: coverage {r.rec.coverage}"
        for r in reviewed
        if r.rec.coverage < floor
    ]


def perturbed(weights: dict[str, float], dim: str, delta: float) -> dict[str, float] | None:
    new = weights[dim] + delta
    if new < 0 or new > 1:
        return None
    rest = 1 - weights[dim]
    scale = (1 - new) / rest if rest else 0
    return {d: new if d == dim else w * scale for d, w in weights.items()}


def sensitivity(recs: list[Recommendation], weights: dict[str, float], top: int = 20):
    """(dimension, delta, companies leaving the top) for each ±10 point weight change."""
    pool = [r for r in recs if r.research_status != ResearchStatus.auto]
    pool = pool if len(pool) >= top else recs
    base = {r.rec.target.ticker for r in rank(pool, weights)[:top]}
    out = []
    for dim in scoring.DIMENSIONS:
        for delta in (-0.10, 0.10):
            w = perturbed(weights, dim, delta)
            if w is None:
                continue
            new = {r.rec.target.ticker for r in rank(pool, w)[:top]}
            out.append((dim, delta, len(base - new)))
    return out
