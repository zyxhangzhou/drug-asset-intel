"""Read-only views over the snapshot for the app pages.

Every entity carries the claims behind its fields (`sources`, grouped by field), loaded in one
query per entity type. Functions return None for an unknown key; the API turns that into 404.
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, col, func, select

from intel.models import (
    Buyer,
    BuyerPreference,
    Catalyst,
    Claim,
    FinancialSnapshot,
    Match,
    Program,
    ProgramIndication,
    Recommendation,
    Source,
    Target,
    Trial,
    TrialResult,
)
from intel.scoring import DIMENSIONS

TOP_MATCHES = 15


class SourceRef(BaseModel):
    source_id: str
    title: str | None
    source_type: str
    publisher: str | None
    published_date: date | None
    published_date_text: str | None
    url: str | None


class ClaimOut(BaseModel):
    value: str | None
    kind: str
    confidence: str | None
    produced_by: str
    model: str | None
    quote: str | None
    as_of: date | None
    note: str | None
    source: SourceRef


Sources = dict[str, list[ClaimOut]]


class Sourced(BaseModel):
    sources: Sources = {}


def claims_by_entity(session: Session, entity_type: str, ids: Iterable[int]) -> dict[int, Sources]:
    """Claims of the given rows of one table, as {row id: {field: [claim]}}."""
    keys = {str(i) for i in ids}
    out: dict[int, Sources] = defaultdict(lambda: defaultdict(list))
    if not keys:
        return out
    rows = session.exec(
        select(Claim, Source)
        .join(Source, col(Claim.source_id) == col(Source.source_id))
        .where(Claim.entity_type == entity_type, col(Claim.entity_id).in_(keys))
        .order_by(col(Claim.id))
    ).all()
    for claim, source in rows:
        out[int(claim.entity_id)][claim.field].append(
            ClaimOut(
                **claim.model_dump(exclude={"source_id"}),
                source=SourceRef(**source.model_dump()),
            )
        )
    return out


def _attach[T: Sourced](
    session: Session, out_cls: type[T], rows: list[SQLModel], **extra_per_row
) -> list[T]:
    if not rows:
        return []
    table = rows[0].__tablename__
    claims = claims_by_entity(session, table, (r.id for r in rows))
    return [
        out_cls(
            **r.model_dump(), **{k: v[i] for k, v in extra_per_row.items()}, sources=claims[r.id]
        )
        for i, r in enumerate(rows)
    ]


# --- buyers ---------------------------------------------------------------------------------


class BuyerSummary(BaseModel):
    ticker: str
    name: str
    name_zh: str | None
    preferences: int
    primary_targets: int  # companies whose primary pair names this buyer


class BuyerOut(Sourced):
    ticker: str
    name: str
    name_zh: str | None
    financial_signals: str | None
    therapeutic_priorities: str | None
    modality_priorities: str | None
    deal_preference: str | None
    buy_rationale: str | None
    key_evidence: str | None
    confidence: str | None


class PreferenceOut(Sourced):
    id: int
    dimension: str
    rank: int
    label: str | None
    need_type: str | None
    target_profile: str | None
    evidence: str | None
    analysis: str | None
    ideal_stage: str | None
    deal_form: str | None
    confidence: str | None


class BuyerFinancialOut(Sourced):
    fiscal_year: str
    currency: str
    revenue_total: float | None
    revenue_us: float | None
    cash_and_short_term_investments: float | None
    total_debt: float | None
    net_debt: float | None
    free_cash_flow: float | None
    capital_allocation_note: str | None
    recent_deals: str | None
    focus_areas: str | None


class LoeProductOut(Sourced):
    product: str
    revenue_global: float | None
    revenue_us: float | None
    us_loe: str | None
    generic_status: str | None
    defense: str | None
    basis_note: str | None


class MatchOut(Sourced):
    ticker: str
    name: str
    shortlisted: bool
    score: float | None
    rationale: str | None
    confidence: str | None


class BuyerDetail(BaseModel):
    buyer: BuyerOut
    preferences: list[PreferenceOut]
    financials: list[BuyerFinancialOut]
    products: list[LoeProductOut]
    matches: list[MatchOut]


def buyers(session: Session) -> list[BuyerSummary]:
    prefs = dict(
        session.exec(
            select(BuyerPreference.buyer_id, func.count()).group_by(BuyerPreference.buyer_id)
        ).all()
    )
    primaries = dict(
        session.exec(
            select(BuyerPreference.buyer_id, func.count())
            .join(Recommendation, col(Recommendation.buyer_preference_id) == BuyerPreference.id)
            .where(Recommendation.is_primary)
            .group_by(BuyerPreference.buyer_id)
        ).all()
    )
    return [
        BuyerSummary(
            ticker=b.ticker,
            name=b.name,
            name_zh=b.name_zh,
            preferences=prefs.get(b.id, 0),
            primary_targets=primaries.get(b.id, 0),
        )
        for b in session.exec(select(Buyer).order_by(Buyer.ticker)).all()
    ]


def buyer_detail(session: Session, ticker: str) -> BuyerDetail | None:
    buyer = session.exec(select(Buyer).where(Buyer.ticker == ticker.upper())).first()
    if buyer is None:
        return None
    prefs = session.exec(
        select(BuyerPreference)
        .where(BuyerPreference.buyer_id == buyer.id)
        # Therapeutic-area rows first, as in the buyer material.
        .order_by(col(BuyerPreference.dimension).desc(), BuyerPreference.rank)
    ).all()
    matches = session.exec(
        select(Match)
        .where(Match.buyer_id == buyer.id, col(Match.score).is_not(None))
        .order_by(col(Match.score).desc(), Match.id)
        .limit(TOP_MATCHES)
    ).all()
    targets = [m.target for m in matches]
    return BuyerDetail(
        buyer=_attach(session, BuyerOut, [buyer])[0],
        preferences=_attach(session, PreferenceOut, list(prefs)),
        financials=_attach(session, BuyerFinancialOut, list(buyer.financials)),
        products=_attach(session, LoeProductOut, list(buyer.products)),
        matches=_attach(
            session,
            MatchOut,
            list(matches),
            ticker=[t.ticker for t in targets],
            name=[t.name for t in targets],
            shortlisted=[t.shortlisted for t in targets],
        ),
    )


# --- companies ------------------------------------------------------------------------------


class TargetOut(Sourced):
    ticker: str
    name: str
    cik: str | None
    excluded: bool
    exclusion_category: str | None
    exclusion_reason: str | None
    shortlisted: bool
    deep_dive: bool
    selection_rationale: str | None


class RecommendationOut(Sourced):
    is_primary: bool
    asset: str | None
    indication: str | None
    therapeutic_area: str | None
    stage: str | None
    buyer_ticker: str | None
    buyer: str | None
    preference: str | None
    scores: dict[str, int | None]
    need_item: str | None
    match_note: str | None
    deal_form: str | None
    design: str | None
    comparability: str | None
    result: str | None
    limitation: str | None
    next_event: str | None
    event_timing: str | None
    event_importance: str | None
    event_certainty: str | None
    enterprise_value: float | None
    rights_status: str | None
    funding_flag: str | None
    thesis: str | None
    conservative: float
    optimistic: float
    coverage: float
    research_status: str


class IndicationOut(Sourced):
    id: int
    indication: str | None
    therapeutic_area: str | None
    stage: str


class ProgramOut(Sourced):
    name: str
    mechanism: str | None
    modality: str | None
    indications: list[IndicationOut]


class ApprovalOut(Sourced):
    application_number: str | None
    brand_name: str | None
    active_ingredients: str | None
    first_approval_date: date | None


class CatalystOut(Sourced):
    program: str | None
    event: str | None
    event_type: str
    window_start: date | None
    window_end: date | None


class FinancialOut(Sourced):
    as_of: date
    currency: str
    cash_and_investments: float | None
    total_debt: float | None
    operating_cash_flow_ytd: float | None
    operating_cash_flow_months: int | None
    runway_months: float | None
    shares_outstanding: float | None
    share_price: float | None
    market_cap: float | None
    acquisition_cost_low: float | None
    acquisition_cost_high: float | None


class TrialSummary(BaseModel):
    nct_id: str
    title: str | None
    phase: str | None
    status: str | None
    enrollment: int | None
    enrollment_type: str | None
    start_date: str | None
    primary_completion_date: str | None
    primary_completion_type: str | None
    expected_readout: str | None
    indication: str | None
    results: int
    source_ids: list[str]  # registry record(s) behind the row; full claims on the trial view


class ResultOut(Sourced):
    nct_id: str
    trial_title: str | None
    endpoint: str | None
    result: str | None
    analysis: str | None
    comparator: str | None
    advantage_vs_soc: str | None


class TargetDetail(BaseModel):
    target: TargetOut
    recommendations: list[RecommendationOut]
    programs: list[ProgramOut]
    approvals: list[ApprovalOut]
    catalysts: list[CatalystOut]
    financial: FinancialOut | None
    trials: list[TrialSummary]
    results: list[ResultOut]


def _recommendations(session: Session, recs: list[Recommendation]) -> list[RecommendationOut]:
    pis = [r.indication for r in recs]
    prefs = [r.preference for r in recs]
    return _attach(
        session,
        RecommendationOut,
        list(recs),
        asset=[pi.program.name if pi else None for pi in pis],
        indication=[pi.indication if pi else None for pi in pis],
        therapeutic_area=[pi.therapeutic_area if pi else None for pi in pis],
        stage=[pi.stage if pi else None for pi in pis],
        buyer_ticker=[p.buyer.ticker if p else None for p in prefs],
        buyer=[p.buyer.name if p else None for p in prefs],
        preference=[p.label if p else None for p in prefs],
        scores=[{d: getattr(r, d) for d in DIMENSIONS} for r in recs],
    )


def _results(session: Session, results: list[TrialResult]) -> list[ResultOut]:
    return _attach(
        session,
        ResultOut,
        results,
        nct_id=[r.trial.nct_id for r in results],
        trial_title=[r.trial.title for r in results],
    )


def target_detail(session: Session, ticker: str) -> TargetDetail | None:
    target = session.exec(select(Target).where(Target.ticker == ticker.upper())).first()
    if target is None:
        return None
    recs = session.exec(
        select(Recommendation)
        .where(Recommendation.target_id == target.id)
        .order_by(col(Recommendation.is_primary).desc(), col(Recommendation.conservative).desc())
    ).all()

    programs = session.exec(
        select(Program).where(Program.target_id == target.id).order_by(Program.name)
    ).all()
    pis = session.exec(
        select(ProgramIndication)
        .where(col(ProgramIndication.program_id).in_([p.id for p in programs]))
        .order_by(ProgramIndication.id)
    ).all()
    pi_out = _attach(session, IndicationOut, list(pis))
    by_program: dict[int, list[IndicationOut]] = defaultdict(list)
    for pi, out in zip(pis, pi_out, strict=True):
        by_program[pi.program_id].append(out)
    program_out = _attach(
        session,
        ProgramOut,
        list(programs),
        indications=[by_program[p.id] for p in programs],
    )

    catalysts = session.exec(
        select(Catalyst)
        .where(Catalyst.target_id == target.id)
        .order_by(Catalyst.window_start, Catalyst.id)
    ).all()
    program_names = {p.id: p.name for p in programs}
    financial = session.exec(
        select(FinancialSnapshot)
        .where(FinancialSnapshot.target_id == target.id)
        .order_by(col(FinancialSnapshot.as_of).desc())
    ).first()

    trials = session.exec(
        select(Trial)
        .where(Trial.target_id == target.id)
        .order_by(col(Trial.start_date).desc(), Trial.nct_id)
    ).all()
    trial_sources: dict[str, set[str]] = defaultdict(set)
    for entity_id, source_id in session.exec(
        select(Claim.entity_id, Claim.source_id)
        .distinct()
        .where(Claim.entity_type == "trial", col(Claim.entity_id).in_([str(t.id) for t in trials]))
    ).all():
        trial_sources[entity_id].add(source_id)
    results = session.exec(
        select(TrialResult)
        .join(Trial)
        .where(Trial.target_id == target.id)
        .order_by(Trial.nct_id, TrialResult.id)
    ).all()
    result_counts: dict[int, int] = defaultdict(int)
    for r in results:
        result_counts[r.trial_id] += 1

    return TargetDetail(
        target=_attach(session, TargetOut, [target])[0],
        recommendations=_recommendations(session, list(recs)),
        programs=program_out,
        approvals=_attach(
            session,
            ApprovalOut,
            sorted(target.approvals, key=lambda a: (a.first_approval_date or date.max, a.id)),
        ),
        catalysts=_attach(
            session,
            CatalystOut,
            list(catalysts),
            program=[program_names.get(c.program_id) for c in catalysts],
        ),
        financial=_attach(session, FinancialOut, [financial])[0] if financial else None,
        trials=[
            TrialSummary(
                **t.model_dump(),
                indication=t.indication.indication if t.indication else None,
                results=result_counts[t.id],
                source_ids=sorted(trial_sources[str(t.id)]),
            )
            for t in trials
        ],
        results=_results(session, list(results)),
    )


# --- trials ---------------------------------------------------------------------------------


class TrialOut(Sourced):
    nct_id: str
    title: str | None
    phase: str | None
    status: str | None
    design: str | None
    conditions: str | None
    interventions: str | None
    enrollment: int | None
    enrollment_type: str | None
    start_date: str | None
    primary_completion_date: str | None
    primary_completion_type: str | None
    completion_date: str | None
    expected_readout: str | None


class TrialDetail(BaseModel):
    trial: TrialOut
    ticker: str
    company: str
    asset: str | None
    indication: IndicationOut | None
    results: list[ResultOut]


def trial_detail(session: Session, nct_id: str) -> TrialDetail | None:
    trial = session.exec(select(Trial).where(Trial.nct_id == nct_id.upper())).first()
    if trial is None:
        return None
    pi = trial.indication
    return TrialDetail(
        trial=_attach(session, TrialOut, [trial])[0],
        ticker=trial.target.ticker,
        company=trial.target.name,
        asset=pi.program.name if pi else None,
        indication=_attach(session, IndicationOut, [pi])[0] if pi else None,
        results=_results(session, list(trial.results)),
    )


# --- sources --------------------------------------------------------------------------------


class SourceDetail(BaseModel):
    source_id: str
    url: str | None
    source_type: str
    title: str | None
    publisher: str | None
    doc_kind: str | None
    note: str | None
    published_date: date | None
    published_date_text: str | None
    fetched_at: datetime
    content_hash: str | None
    link_status: str
    has_text: bool
    claims: int


def archived_text_path(source: Source, raw_dir: Path) -> Path | None:
    """The archived .txt of a source, only when it resolves inside the raw data directory."""
    if not source.local_path or not source.local_path.endswith(".txt"):
        return None
    path = Path(source.local_path).resolve()
    if not path.is_relative_to(raw_dir.resolve()) or not path.is_file():
        return None
    return path


def source_detail(session: Session, source_id: str, raw_dir: Path) -> SourceDetail | None:
    source = session.get(Source, source_id)
    if source is None:
        return None
    claims = session.exec(
        select(func.count()).select_from(Claim).where(Claim.source_id == source_id)
    ).one()
    return SourceDetail(
        **source.model_dump(exclude={"fetched_at"}),
        # SQLite drops tzinfo; fetch times are always written in UTC.
        fetched_at=source.fetched_at.replace(tzinfo=UTC),
        has_text=archived_text_path(source, raw_dir) is not None,
        claims=claims,
    )


def source_text(session: Session, source_id: str, raw_dir: Path) -> str | None:
    source = session.get(Source, source_id)
    path = archived_text_path(source, raw_dir) if source else None
    return path.read_text(encoding="utf-8") if path else None
