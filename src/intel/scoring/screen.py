"""Build step: score recommendation pairs, apply analyst reviews, pick the shortlist.

Rules: docs/scoring-rules.md. Auto screening uses structured snapshot data only; a signed
review file replaces the auto values for its company.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from sqlmodel import select

from intel import scoring
from intel.enums import (
    ClaimKind,
    Confidence,
    EventCertainty,
    EventImportance,
    ProducedBy,
    ResearchStatus,
    RightsStatus,
    Stage,
)
from intel.ingest import SNAPSHOT_DATE, BuildContext
from intel.models import (
    BuyerPreference,
    Claim,
    FinancialSnapshot,
    Match,
    ProgramIndication,
    Recommendation,
    Source,
    Target,
    Trial,
)
from intel.scoring import taxonomy
from intel.scoring.review import Review, ReviewError, load_manual_sources, load_reviews

IMPORTANCE_BY_PHASE = {
    Stage.phase3: EventImportance.high,
    Stage.phase2_3: EventImportance.high,
    Stage.phase2: EventImportance.medium,
}
IMPORTANCE_ZH = {"high": "高", "medium": "中", "low": "低"}
P_VALUE = re.compile(r"p\s*([<=≤])\s*(0?\.\d+)")


class Sources:
    """Claim source ids per (entity, id, field), loaded once."""

    def __init__(self, session):
        self.by_key: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for et, eid, fld, sid in session.exec(
            select(Claim.entity_type, Claim.entity_id, Claim.field, Claim.source_id)
        ):
            if sid not in self.by_key[(et, eid, fld)]:
                self.by_key[(et, eid, fld)].append(sid)

    def of(self, entity: str, entity_id, *fields: str) -> list[str]:
        out: list[str] = []
        for f in fields:
            for sid in self.by_key[(entity, str(entity_id), f)]:
                if sid not in out:
                    out.append(sid)
        return out


@dataclass
class Cell:
    """A business value with its sources and labels, before it is written."""

    value: object
    sources: list[str]
    kind: ClaimKind = ClaimKind.inference
    confidence: Confidence | None = Confidence.medium
    note: str | None = None


@dataclass
class Pair:
    target: Target
    pi: ProgramIndication | None
    pref: BuyerPreference | None
    pmap: taxonomy.PreferenceMap | None
    cells: dict[str, Cell] = field(default_factory=dict)
    event_importance: EventImportance | None = None
    event_certainty: EventCertainty | None = None
    status: ResearchStatus = ResearchStatus.auto
    conservative: float = 0.0
    optimistic: float = 0.0
    coverage: float = 0.0

    def score(self, dim: str) -> int | None:
        cell = self.cells.get(dim)
        return None if cell is None else cell.value

    def scores(self) -> dict[str, int | None]:
        return {d: self.score(d) for d in scoring.DIMENSIONS}


def significant(analysis: str | None) -> bool:
    for op, value in P_VALUE.findall((analysis or "").lower()):
        if (op in "<≤" and float(value) <= 0.05) or (op == "=" and float(value) < 0.05):
            return True
    return False


def months_after(start: date, text: str | None) -> float | None:
    if not text:
        return None
    parts = text.split("-")
    try:
        year, month = int(parts[0]), int(parts[1])
    except (IndexError, ValueError):
        return None
    return (year - start.year) * 12 + (month - start.month)


class Scorer:
    def __init__(self, ctx: BuildContext, cfg: scoring.ScoringConfig):
        self.ctx, self.cfg = ctx, cfg
        self.src = Sources(ctx.session)
        self.trials: dict[int, list[Trial]] = defaultdict(list)
        for trial in ctx.session.exec(select(Trial).where(Trial.indication_id.is_not(None))):
            self.trials[trial.indication_id].append(trial)

    # --- auto dimensions -----------------------------------------------------------------

    def buyer_fit(self, pair: Pair) -> Cell | None:
        if pair.pi is None:
            return None
        if pair.pref is None:
            return Cell(
                0,
                self.src.of("program_indication", pair.pi.id, "indication"),
                note="自动初筛：资产治疗领域不在任何买方偏好中",
            )
        areas = set((pair.pi.therapeutic_area or "").split(";")) & pair.pmap.ta_codes
        sources = self.src.of("buyer_preference", pair.pref.id, "label") + self.src.of(
            "program_indication", pair.pi.id, "therapeutic_area"
        )
        return Cell(
            scoring.AUTO_CAPS["buyer_fit"],
            sources,
            note=f"自动初筛：治疗领域 {', '.join(sorted(areas))} 与偏好「{pair.pref.label}」相交；"
            "只是标签匹配，上限 2 分",
        )

    def stage_match(self, pair: Pair) -> Cell | None:
        if pair.pi is None or pair.pmap is None:
            return (
                Cell(
                    0,
                    self.src.of("program_indication", pair.pi.id, "stage"),
                    note="没有匹配的买方偏好",
                )
                if pair.pi
                else None
            )
        score = scoring.stage_match(pair.pi.stage, pair.pmap.stage_min, pair.pmap.stage_max)
        if score is None:
            return None
        sources = self.src.of("buyer_preference", pair.pref.id, "ideal_stage") + self.src.of(
            "program_indication", pair.pi.id, "stage"
        )
        return Cell(
            score,
            sources,
            note=f"资产阶段 {pair.pi.stage}（CT.gov 推导）；偏好区间 "
            f"{pair.pmap.stage_min}–{pair.pmap.stage_max}（「{pair.pref.ideal_stage}」）",
        )

    def clinical(self, pair: Pair) -> dict[str, Cell]:
        if pair.pi is None:
            return {}
        for trial in self.trials[pair.pi.id]:
            if scoring.STAGE_ORDER.get(trial.phase, 0) < 2:
                continue
            for result in trial.results:
                if significant(result.analysis):
                    sources = [f"CTG-{trial.nct_id}"]
                    return {
                        "clinical": Cell(
                            scoring.AUTO_CAPS["clinical"],
                            sources,
                            note="自动初筛：主要终点统计分析 p < 0.05；"
                            "未判断临床意义与可比性，上限 2 分",
                        ),
                        "design": Cell(
                            f"{trial.nct_id}：{trial.design}", sources, ClaimKind.fact, None
                        ),
                        "result": Cell(
                            f"{result.endpoint}：{result.analysis}", sources, ClaimKind.fact, None
                        ),
                    }
        return {}

    def catalyst(self, pair: Pair) -> dict[str, Cell]:
        if pair.pi is None:
            return {}
        best = None
        for trial in self.trials[pair.pi.id]:
            if trial.primary_completion_type != "ESTIMATED":
                continue
            ahead = months_after(SNAPSHOT_DATE, trial.primary_completion_date)
            if ahead is None or not 0 <= ahead <= self.cfg.catalyst_window_months:
                continue
            importance = IMPORTANCE_BY_PHASE.get(trial.phase, EventImportance.low)
            key = (scoring.catalyst_score(importance, EventCertainty.estimated), -ahead)
            if best is None or key > best[0]:
                best = (key, trial, importance)
        if best is None:
            # The registry shows no estimated completion in the window: a sourced zero, which a
            # review can raise with a company-disclosed event.
            sources = [f"CTG-{t.nct_id}" for t in self.trials[pair.pi.id]]
            if not sources:
                return {}
            return {
                "catalyst": Cell(
                    0,
                    sources,
                    note=f"CT.gov 中该资产适应症没有预计在 {self.cfg.catalyst_window_months} 个月内"
                    "完成的试验；公司披露的事件待复核",
                )
            }
        _, trial, importance = best
        sources = [f"CTG-{trial.nct_id}"]
        pair.event_importance, pair.event_certainty = importance, EventCertainty.estimated
        return {
            "catalyst": Cell(
                best[0][0],
                sources,
                note=f"重要性{IMPORTANCE_ZH[importance]}（按登记阶段）× 登记估算",
            ),
            "next_event": Cell(
                f"{trial.nct_id}（{trial.phase}）主要终点数据（估算）",
                sources,
                note="读出时间按 CT.gov 预计主要完成日期估算，不是公司披露",
            ),
            "event_timing": Cell(
                trial.primary_completion_date,
                sources,
                ClaimKind.fact,
                None,
                note="CT.gov 预计主要完成日期（ESTIMATED）",
            ),
        }

    def money(self, pair: Pair, fin: FinancialSnapshot | None) -> dict[str, Cell]:
        if fin is None:
            return {}
        cells: dict[str, Cell] = {}
        if fin.market_cap is not None and fin.cash_and_investments is not None:
            debt = fin.total_debt or 0.0
            ev = fin.market_cap + debt - fin.cash_and_investments
            sources = self.src.of(
                "financial_snapshot", fin.id, "market_cap", "cash_and_investments", "total_debt"
            )
            debt_note = "" if fin.total_debt is not None else "；未申报债务，按 0 计"
            cells["enterprise_value"] = Cell(
                round(ev), sources, note=f"EV = 市值 + 债务 − 现金及投资{debt_note}"
            )
            score = scoring.dealability(ev, None, self.cfg.ev_tiers)
            cells["dealability"] = Cell(
                score, sources, note=f"EV {ev / 1e8:,.1f} 亿美元；资产权益待核实"
            )
        if fin.operating_cash_flow_ytd is not None and fin.operating_cash_flow_ytd >= 0:
            flag = "自给"
        elif fin.runway_months is not None and fin.runway_months < self.cfg.funding_pressure_months:
            flag = "融资压力"
        elif fin.runway_months is not None:
            flag = f"可支撑约 {fin.runway_months:.0f} 个月"
        else:
            flag = None
        if flag:
            cells["funding_flag"] = Cell(
                flag,
                self.src.of(
                    "financial_snapshot", fin.id, "runway_months", "operating_cash_flow_ytd"
                ),
                note="提示，不计分；资金紧张不解释为容易收购",
            )
        return cells

    def auto(self, pair: Pair, fin: FinancialSnapshot | None) -> Pair:
        for name, cell in (
            ("buyer_fit", self.buyer_fit(pair)),
            ("stage_match", self.stage_match(pair)),
        ):
            if cell is not None:
                pair.cells[name] = cell
        pair.cells.update(self.clinical(pair))
        pair.cells.update(self.catalyst(pair))
        pair.cells.update(self.money(pair, fin))
        return pair

    # --- totals --------------------------------------------------------------------------

    def finish(self, pair: Pair, fin: FinancialSnapshot | None) -> Pair:
        weights = self.cfg.weights
        pair.conservative = scoring.conservative(pair.scores(), weights)
        pair.optimistic = scoring.optimistic(pair.scores(), weights)
        has = lambda name: name in pair.cells and pair.cells[name].value not in (None, "")  # noqa: E731
        pi_ok = pair.pi is not None
        required = [
            pi_ok,  # asset
            pi_ok and bool(self.src.of("program_indication", pair.pi.id, "indication")),
            pi_ok and pair.pi.stage != Stage.unknown,
            has("need_item"),
            has("match_note"),
            has("design"),
            has("result"),
            has("next_event"),
            has("enterprise_value"),
            has("rights_status"),
        ]
        pair.coverage = round(sum(map(bool, required)) / len(required), 2)
        return pair


def candidate_pairs(target, prefs, financial, scorer) -> list[Pair]:
    pis = [
        pi for program in target.programs for pi in program.indications if pi.stage != Stage.unknown
    ]
    pairs = []
    for pi in pis:
        areas = set((pi.therapeutic_area or "").split(";")) - {""}
        for pref, pmap in prefs:
            if areas & pmap.ta_codes:
                pairs.append(scorer.auto(Pair(target, pi, pref, pmap), financial))
    if not pairs:
        top = max(pis, key=lambda p: (scoring.STAGE_ORDER[p.stage], -p.id), default=None)
        pairs.append(scorer.auto(Pair(target, top, None, None), financial))
    return [scorer.finish(p, financial) for p in pairs]


def pick_primary(pairs: list[Pair]) -> Pair:
    return max(
        pairs,
        key=lambda p: (
            p.conservative,
            p.coverage,
            scoring.STAGE_ORDER.get(p.pi.stage, -1) if p.pi else -1,
            -(p.pref.rank if p.pref else 9),  # a buyer's first priority beats its third
            -(p.pi.id if p.pi else 0),
            -(p.pref.id if p.pref else 0),
        ),
    )


# --- reviews ------------------------------------------------------------------------------


def reviewed_pair(review: Review, target, prefs, financial, scorer) -> Pair:
    needle = review.program.lower()
    pis = [
        pi
        for program in target.programs
        if needle in program.name.lower()
        for pi in program.indications
        if review.indication is None or review.indication.lower() in (pi.indication or "").lower()
    ]
    if not pis:
        raise ReviewError(
            f"{review.path.name}: no derived program matches "
            f"{review.program!r} / {review.indication!r}"
        )
    pi = max(pis, key=lambda p: (scoring.STAGE_ORDER.get(p.stage, -1), -p.id))
    pref = pmap = None
    if review.buyer:
        found = [
            (p, m)
            for p, m in prefs
            if p.buyer.name == review.buyer and p.rank == review.preference_rank
        ]
        if not found:
            raise ReviewError(
                f"{review.path.name}: no verified preference "
                f"{review.buyer!r} #{review.preference_rank}"
            )
        pref, pmap = found[0]
    pair = scorer.auto(Pair(target, pi, pref, pmap), financial)
    pair.status = review.status
    for dim, scored in review.scores.items():
        pair.cells[dim] = Cell(
            scored.score, scored.sources, confidence=scored.confidence, note=scored.reason
        )
    fit_sources = review.scores["buyer_fit"].sources if "buyer_fit" in review.scores else []
    for name, text, kind in (
        ("need_item", review.need_item, ClaimKind.fact),
        ("match_note", review.match_note, ClaimKind.inference),
        ("deal_form", review.deal_form, ClaimKind.inference),
    ):
        if text:
            pair.cells[name] = Cell(
                text, fit_sources, kind, None if kind == ClaimKind.fact else Confidence.medium
            )
    if review.clinical:
        for name in ("design", "comparability", "result", "limitation"):
            if name in review.clinical.values:
                fact = name in ("design", "result")
                pair.cells[name] = Cell(
                    review.clinical.values[name],
                    review.clinical.sources,
                    ClaimKind.fact if fact else ClaimKind.inference,
                    None if fact else Confidence.medium,
                )
    if review.event:
        disclosed = review.event_certainty == EventCertainty.disclosed
        kind, conf = (
            (ClaimKind.fact, None) if disclosed else (ClaimKind.inference, Confidence.medium)
        )
        for name, key in (("next_event", "text"), ("event_timing", "timing")):
            if key in review.event.values:
                pair.cells[name] = Cell(review.event.values[key], review.event.sources, kind, conf)
        pair.event_importance, pair.event_certainty = (
            review.event_importance,
            review.event_certainty,
        )
        if "catalyst" not in review.scores:
            pair.cells["catalyst"] = Cell(
                scoring.catalyst_score(review.event_importance, review.event_certainty),
                review.event.sources,
                note=f"重要性 × 确定性：{review.event_importance} × {review.event_certainty}",
            )
    if review.rights:
        cited = review.rights_cited
        note = cited.values.get("note") if cited else None
        pair.cells["rights_status"] = Cell(
            review.rights,
            cited.sources if cited else [],
            confidence=Confidence.medium_high,
            note=note,
        )
        ev = pair.cells.get("enterprise_value")
        if "dealability" not in review.scores and ev is not None:
            pair.cells["dealability"] = Cell(
                scoring.dealability(ev.value, review.rights, scorer.cfg.ev_tiers),
                ev.sources + (cited.sources if cited else []),
                note=f"EV 档位，资产权益「{review.rights}」封顶",
            )
    if review.thesis:
        pair.cells["thesis"] = Cell(review.thesis, review.thesis_sources)
    return scorer.finish(pair, financial)


def shortlist_blocker(pair: Pair) -> str | None:
    if pair.status == ResearchStatus.auto:
        return "未复核"
    rights = (pair.cells.get("rights_status") or Cell(None, [])).value
    if rights is None:
        return "资产权益待核实"
    deal_form = (pair.cells.get("deal_form") or Cell("", [])).value or ""
    if rights == RightsStatus.restricted and "收购" in deal_form:
        return "资产权益受限，与收购方案不兼容"
    thesis = pair.cells.get("thesis")
    if thesis is None or not thesis.sources:
        return "缺两句话论点或其来源"
    return None


# --- writing ------------------------------------------------------------------------------


def write_pair(ctx: BuildContext, pair: Pair, primary: bool) -> Recommendation:
    rec = Recommendation(
        target_id=pair.target.id,
        program_indication_id=pair.pi.id if pair.pi else None,
        buyer_preference_id=pair.pref.id if pair.pref else None,
        is_primary=primary,
        event_importance=pair.event_importance,
        event_certainty=pair.event_certainty,
        conservative=pair.conservative,
        optimistic=pair.optimistic,
        coverage=pair.coverage,
        research_status=pair.status,
    )
    for name, cell in pair.cells.items():
        setattr(rec, name, cell.value)
    ctx.session.add(rec)
    ctx.session.flush()
    produced = ProducedBy.api if pair.status == ResearchStatus.auto else ProducedBy.manual
    for name, cell in pair.cells.items():
        if cell.value in (None, ""):
            continue
        if not cell.sources:
            raise ReviewError(f"{pair.target.ticker}: {name} has a value but no source")
        for sid in cell.sources:
            ctx.claim(
                "recommendation",
                rec.id,
                name,
                cell.value,
                sid,
                kind=cell.kind,
                confidence=cell.confidence if cell.kind == ClaimKind.inference else None,
                produced_by=produced,
                note=cell.note,
            )
    return rec


def _register_manual_sources(ctx: BuildContext, reviews: dict[str, Review]) -> None:
    for source in load_manual_sources(ctx.inputs.manual_sources):
        ctx.session.add(source)
    ctx.session.flush()
    known = set(ctx.session.exec(select(Source.source_id)).all())
    for review in reviews.values():
        missing = sorted(review.all_sources() - known)
        if missing:
            raise ReviewError(f"{review.path.name}: unregistered source id(s) {', '.join(missing)}")


LONGLIST_HEADER = [
    "rank_optimistic", "ticker", "name", "conservative", "optimistic", "coverage",
    "research_status", "asset", "indication", "stage", "therapeutic_area", "buyer",
    "preference", *scoring.DIMENSIONS, "next_event", "event_timing", "enterprise_value",
    "rights_status", "funding_flag", "in_longlist", "shortlisted", "not_shortlisted_reason",
]  # fmt: skip


def ingest(ctx: BuildContext) -> None:
    cfg = scoring.ScoringConfig.load(ctx.inputs.scoring_config)
    reviews = load_reviews(ctx.inputs.reviews_dir)
    _register_manual_sources(ctx, reviews)
    prefs = taxonomy.mapped_preferences(ctx)
    if not prefs:
        ctx.notes.append("no verified buyer preference map: every pair has no buyer")
    scorer = Scorer(ctx, cfg)
    session = ctx.session
    targets = session.exec(select(Target).where(Target.excluded == False)).all()  # noqa: E712
    primaries: list[tuple[Pair, list[Pair]]] = []
    for target in targets:
        fin = target.financials[0] if target.financials else None
        pairs = candidate_pairs(target, prefs, fin, scorer)
        review = reviews.pop(target.ticker, None)
        if review:
            primary = reviewed_pair(review, target, prefs, fin, scorer)
        else:
            primary = pick_primary(pairs)
        others = _best_per_buyer(pairs, primary)
        primaries.append((primary, others))
    if reviews:
        raise ReviewError(f"review files for unknown tickers: {', '.join(sorted(reviews))}")

    blockers = {id(p): shortlist_blocker(p) for p, _ in primaries}
    eligible = sorted(
        (p for p, _ in primaries if blockers[id(p)] is None), key=lambda p: -p.conservative
    )
    shortlisted = {id(p) for p in eligible[: cfg.shortlist_max]}
    by_optimistic = sorted(
        primaries, key=lambda x: (-x[0].optimistic, -x[0].conservative, x[0].target.ticker)
    )
    # A company without any derived asset has nothing to research toward a pair.
    with_asset = [id(p) for p, _ in by_optimistic if p.pi is not None]
    longlist = set(with_asset[: cfg.longlist_size])

    rows = [LONGLIST_HEADER]
    short_rows = [["rank", "ticker", "name", "conservative", "optimistic", "coverage",
                   "research_status", "buyer", "asset", "indication", "thesis"]]  # fmt: skip
    for rank, (primary, others) in enumerate(by_optimistic, 1):
        write_pair(ctx, primary, primary=True)
        for other in others:
            write_pair(ctx, other, primary=False)
        _write_matches(ctx, scorer, [primary, *others])
        if id(primary) in shortlisted:
            _mark_shortlisted(ctx, primary)
        rows.append(
            _row(
                rank,
                primary,
                id(primary) in longlist,
                id(primary) in shortlisted,
                blockers[id(primary)],
            )
        )
    for rank, pair in enumerate(eligible[: cfg.shortlist_max], 1):
        short_rows.append([
            rank, pair.target.ticker, pair.target.name, pair.conservative, pair.optimistic,
            pair.coverage, pair.status, _buyer_name(pair), _asset(pair),
            pair.pi.indication if pair.pi else "", pair.cells["thesis"].value,
        ])  # fmt: skip
    ctx.outputs["longlist.csv"] = rows
    ctx.outputs["shortlist.csv"] = short_rows


def _best_per_buyer(pairs: list[Pair], primary: Pair) -> list[Pair]:
    best: dict[int, Pair] = {}
    for p in pairs:
        if p.pref is None or p is primary:
            continue
        if primary.pref and p.pref.buyer_id == primary.pref.buyer_id:
            continue
        cur = best.get(p.pref.buyer_id)
        if cur is None or pick_primary([cur, p]) is p:
            best[p.pref.buyer_id] = p
    return [best[k] for k in sorted(best)]


def _write_matches(ctx: BuildContext, scorer: Scorer, pairs: list[Pair]) -> None:
    for pair in pairs:
        if pair.pref is None:
            continue
        rationale = (
            f"{_asset(pair)}（{pair.pi.indication}，{pair.pi.stage}）对应偏好「{pair.pref.label}」；"
            f"保守分 {pair.conservative}"
        )
        match = Match(
            buyer_id=pair.pref.buyer_id,
            target_id=pair.target.id,
            score=pair.conservative,
            rationale=rationale,
            confidence=Confidence.medium if pair.status != ResearchStatus.auto else Confidence.low,
        )
        ctx.session.add(match)
        ctx.session.flush()
        sources = scorer.src.of("buyer_preference", pair.pref.id, "label") + scorer.src.of(
            "program_indication", pair.pi.id, "indication"
        )
        for field_name, value in (("score", match.score), ("rationale", rationale)):
            for sid in sources:
                ctx.claim("match", match.id, field_name, value, sid, kind=ClaimKind.inference,
                          confidence=match.confidence, produced_by=ProducedBy.api,
                          note="买方 × 标的最佳组合的保守分")  # fmt: skip


def _mark_shortlisted(ctx: BuildContext, pair: Pair) -> None:
    pair.target.shortlisted = True
    thesis = pair.cells["thesis"]
    pair.target.selection_rationale = thesis.value
    for sid in thesis.sources:
        ctx.claim("target", pair.target.id, "selection_rationale", thesis.value, sid,
                  kind=ClaimKind.inference, confidence=Confidence.medium,
                  produced_by=ProducedBy.manual, note="两句话入选论点（人工复核）")  # fmt: skip


def _asset(pair: Pair) -> str:
    return pair.pi.program.name if pair.pi else ""


def _buyer_name(pair: Pair) -> str:
    return pair.pref.buyer.name if pair.pref else ""


def _row(rank, pair: Pair, in_longlist: bool, shortlisted: bool, blocker) -> list:
    cell = lambda n: "" if pair.cells.get(n) is None else pair.cells[n].value  # noqa: E731
    return [
        rank, pair.target.ticker, pair.target.name, pair.conservative, pair.optimistic,
        pair.coverage, pair.status, _asset(pair), pair.pi.indication if pair.pi else "",
        pair.pi.stage if pair.pi else "", pair.pi.therapeutic_area if pair.pi else "",
        _buyer_name(pair), f"#{pair.pref.rank} {pair.pref.label}" if pair.pref else "",
        *[("" if pair.score(d) is None else pair.score(d)) for d in scoring.DIMENSIONS],
        cell("next_event"), cell("event_timing"), cell("enterprise_value"),
        cell("rights_status") or "待核实", cell("funding_flag"),
        in_longlist, shortlisted,
        "" if shortlisted else ("无推导管线" if pair.pi is None else blocker or "名额已满"),
    ]  # fmt: skip
