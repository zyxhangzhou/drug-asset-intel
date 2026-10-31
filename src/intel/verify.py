"""Stratified random sample of snapshot claims for verification, and the user spot-check list.

Three layers: structured (official-interface facts, checked here against the cached raw responses
with reading code independent of the ingest modules), review (analyst review files) and LLM
(signed extractions); the last two are checked by people. Same snapshot and seed, same sample.
"""

import csv
import json
import random
import tomllib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, col, select

from intel.models import (
    ApprovedProduct,
    Catalyst,
    Claim,
    FinancialSnapshot,
    Program,
    Recommendation,
    SnapshotMeta,
    Source,
    Target,
    Trial,
    TrialResult,
)

SEED = 20261101
PER_LAYER = 30

# Structured strata: source type -> (entity table, fields the raw response can confirm).
STRATA: dict[str, tuple[str, set[str]]] = {
    "ctgov": (
        "trial",
        {
            "title",
            "phase",
            "status",
            "start_date",
            "primary_completion_date",
            "completion_date",
            "enrollment",
        },
    ),  # fmt: skip
    "sec_xbrl": (
        "financial_snapshot",
        {"cash_and_investments", "operating_cash_flow_ytd", "shares_outstanding", "total_debt"},
    ),
    "market_data": ("financial_snapshot", {"share_price"}),
    "openfda": (
        "approved_product",
        {"application_number", "brand_name", "active_ingredients", "first_approval_date"},
    ),
}
REVIEW_ENTITIES = ("recommendation", "financial_snapshot")

HEADER = [
    "layer", "stratum", "claim_id", "ticker", "entity_type", "entity_id", "field", "value", "kind",
    "confidence", "source_id", "source_type", "url", "local_path", "quote", "note",
    "auto_check", "auto_detail", "verdict", "error_type", "checker_note",
]  # fmt: skip


@dataclass
class Row:
    layer: str
    stratum: str
    claim: Claim
    source: Source
    ticker: str
    auto_check: str = ""
    auto_detail: str = ""
    extra: dict = field(default_factory=dict)

    def cells(self) -> list:
        c, s = self.claim, self.source
        return [
            self.layer, self.stratum, c.id, self.ticker, c.entity_type, c.entity_id, c.field,
            c.value, c.kind, c.confidence or "", s.source_id, s.source_type, s.url or "",
            s.local_path or "", c.quote or "", c.note or "", self.auto_check, self.auto_detail,
            "", "", "",
        ]  # fmt: skip


def _claims(session: Session, *where) -> list[tuple[Claim, Source]]:
    return list(
        session.exec(
            select(Claim, Source)
            .join(Source, col(Claim.source_id) == col(Source.source_id))
            .where(*where)
            .order_by(col(Claim.id))
        ).all()
    )


def _ticker(session: Session, entity: str, entity_id: str) -> str:
    key = int(entity_id)
    match entity:
        case "trial":
            target_id = session.get(Trial, key).target_id
        case "trial_result":
            target_id = session.get(Trial, session.get(TrialResult, key).trial_id).target_id
        case "financial_snapshot":
            target_id = session.get(FinancialSnapshot, key).target_id
        case "approved_product":
            target_id = session.get(ApprovedProduct, key).target_id
        case "recommendation":
            target_id = session.get(Recommendation, key).target_id
        case "catalyst":
            target_id = session.get(Catalyst, key).target_id
        case "program":
            target_id = session.get(Program, key).target_id
        case _:
            raise ValueError(f"no ticker lookup for {entity}")
    return session.get(Target, target_id).ticker


def sample(session: Session, per_layer: int = PER_LAYER, seed: int = SEED) -> list[Row]:
    rng = random.Random(seed)
    rows: list[Row] = []
    quota = [per_layer // len(STRATA) + (i < per_layer % len(STRATA)) for i in range(len(STRATA))]
    for (stype, (entity, fields)), k in zip(STRATA.items(), quota, strict=True):
        pool = _claims(
            session,
            Claim.produced_by == "api",
            Claim.kind == "fact",
            Claim.entity_type == entity,
            col(Claim.field).in_(fields),
            Source.source_type == stype,
        )
        rows += [Row("structured", stype, c, s, "") for c, s in rng.sample(pool, min(k, len(pool)))]
    review = _claims(
        session, Claim.produced_by == "manual", col(Claim.entity_type).in_(REVIEW_ENTITIES)
    )
    rows += [
        Row("review", "", c, s, "") for c, s in rng.sample(review, min(per_layer, len(review)))
    ]
    llm = _claims(session, Claim.produced_by == "llm")
    rows += [Row("llm", "", c, s, "") for c, s in rng.sample(llm, min(per_layer, len(llm)))]
    for r in rows:
        r.ticker = _ticker(session, r.claim.entity_type, r.claim.entity_id)
    return rows


# --- structured layer: compare with the cached raw responses -----------------------------------

PHASE = {
    ("EARLY_PHASE1",): "phase1", ("PHASE1",): "phase1", ("PHASE1", "PHASE2"): "phase1_2",
    ("PHASE2",): "phase2", ("PHASE2", "PHASE3"): "phase2_3", ("PHASE3",): "phase3",
    ("PHASE4",): "approved",
}  # fmt: skip


def _same_number(a: str, b: float, tol: float = 0.5) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def _check_ctgov(raw: Path, row: Row, session: Session) -> tuple[str, str]:
    trial = session.get(Trial, int(row.claim.entity_id))
    path = raw / "ctgov" / f"{row.ticker}.json"
    if not path.exists():
        return "无法比对", f"缺少缓存 {path.name}"
    studies = json.loads(path.read_text(encoding="utf-8"))["studies"]
    study = next(
        (
            s["protocolSection"]
            for s in studies
            if s["protocolSection"]["identificationModule"]["nctId"] == trial.nct_id
        ),
        None,
    )
    if study is None:
        return "无法比对", f"缓存中没有 {trial.nct_id}"
    status, design = study.get("statusModule", {}), study.get("designModule", {})
    ident = study["identificationModule"]
    value = row.claim.value
    match row.claim.field:
        case "title":
            raw_values = [ident.get("briefTitle"), ident.get("officialTitle")]
        case "phase":
            raw_values = [PHASE.get(tuple(sorted(design.get("phases") or [])), "unknown")]
        case "status":
            raw_values = [status.get("overallStatus")]
        case "enrollment":
            raw_values = [str((design.get("enrollmentInfo") or {}).get("count"))]
        case name:
            key = {
                "start_date": "startDateStruct",
                "primary_completion_date": "primaryCompletionDateStruct",
                "completion_date": "completionDateStruct",
            }[name]
            raw_values = [(status.get(key) or {}).get("date")]
    ok = value in raw_values
    return ("一致" if ok else "不一致"), f"缓存值：{' | '.join(str(v) for v in raw_values)}"


def _xbrl_values(facts: dict) -> list[tuple[str, str, float]]:
    out = []
    for taxonomy in ("us-gaap", "dei"):
        for tag, units in facts.get(taxonomy, {}).items():
            for points in units.values():
                out += [(tag, p.get("end", ""), float(p["val"])) for p in points]
    return out


def _check_xbrl(raw: Path, row: Row, session: Session) -> tuple[str, str]:
    snap = session.get(FinancialSnapshot, int(row.claim.entity_id))
    cik = session.get(Target, snap.target_id).cik
    path = raw / "sec" / "companyfacts" / f"{cik}.json"
    if not cik or not path.exists():
        return "无法比对", "缺少 companyfacts 缓存"
    points = _xbrl_values(json.loads(path.read_text(encoding="utf-8")))
    value = float(row.claim.value)
    if row.claim.field == "shares_outstanding":
        hits = [t for t, _, v in points if abs(v - value) <= 0.5]
    else:
        as_of = snap.as_of.isoformat()
        same_day = [(t, v) for t, end, v in points if end == as_of]
        hits = [t for t, v in same_day if abs(v - value) <= 0.5]
        if not hits:  # debt is often filed as current + non-current
            hits = [
                f"{a}+{b}"
                for i, (a, x) in enumerate(same_day)
                for b, y in same_day[i + 1 :]
                if abs(x + y - value) <= 0.5
            ]
    if hits:
        return "一致", f"见标签 {hits[0]}"
    return "不一致", f"{snap.as_of} 无此值"


def _check_price(raw: Path, row: Row, session: Session) -> tuple[str, str]:
    meta = session.get(SnapshotMeta, 1)
    path = raw / "nasdaq" / f"{row.ticker}.json"
    if not path.exists() or not meta or not meta.snapshot_date:
        return "无法比对", "缺少行情缓存或快照日"
    closes = {
        datetime.strptime(r["date"], "%m/%d/%Y").date(): float(
            r["close"].strip("$").replace(",", "")
        )
        for r in json.loads(path.read_text(encoding="utf-8"))["rows"]
        if r.get("close")
    }
    on_or_before = [d for d in closes if d <= meta.snapshot_date]
    if not on_or_before:
        return "无法比对", "快照日前没有收盘价"
    day = max(on_or_before)
    ok = _same_number(row.claim.value, closes[day], tol=0.005)
    return ("一致" if ok else "不一致"), f"{day} 收盘 {closes[day]}"


def _check_openfda(raw: Path, row: Row, session: Session) -> tuple[str, str]:
    product = session.get(ApprovedProduct, int(row.claim.entity_id))
    apps = json.loads((raw / "openfda" / "drugsfda_nda_bla.json").read_text(encoding="utf-8"))
    app = next(
        (a for a in apps["applications"] if a["application_number"] == product.application_number),
        None,
    )
    if app is None:
        return "不一致", f"导出中没有 {product.application_number}"
    value = row.claim.value
    match row.claim.field:
        case "application_number":
            ok = value == app["application_number"]
            return ("一致" if ok else "不一致"), f"缓存申请号：{app['application_number']}"
        case "brand_name":
            names = {p.get("brand_name") for p in app.get("products", [])}
            return (
                "一致" if value in names else "不一致"
            ), f"缓存商品名：{', '.join(map(str, names))}"
        case "active_ingredients":
            found = {a for p in app.get("products", []) for a in p.get("active_ingredients") or []}
            ours = {x.strip() for x in value.split(";")} if ";" in value else {value.strip()}
            ok = ours <= found or {x.strip() for x in value.split(",")} <= found
            return ("一致" if ok else "不一致"), f"缓存成分：{', '.join(sorted(found))}"
        case _:
            approved = sorted(
                s["submission_status_date"]
                for s in app.get("submissions", [])
                if s.get("submission_status") == "AP" and s.get("submission_status_date")
            )
            first = approved[0] if approved else None
            iso = f"{first[:4]}-{first[4:6]}-{first[6:]}" if first and "-" not in first else first
            return ("一致" if value == iso else "不一致"), f"最早批准日：{iso}"


CHECKS = {
    "ctgov": _check_ctgov,
    "sec_xbrl": _check_xbrl,
    "market_data": _check_price,
    "openfda": _check_openfda,
}


def auto_check(session: Session, rows: list[Row], raw: Path) -> None:
    for r in rows:
        if r.layer == "structured":
            r.auto_check, r.auto_detail = CHECKS[r.stratum](raw, r, session)


def write_sheet(rows: list[Row], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        w.writerows(r.cells() for r in rows)
    return out


# --- user spot check ----------------------------------------------------------------------------


def spot_check(reviews_dir: Path, session: Session, n: int = 5, seed: int = SEED) -> str:
    """Markdown checklist for the user: n signed review files picked with the fixed seed."""
    signed = []
    for path in sorted(reviews_dir.glob("*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        if str(data.get("verified_by", "")).strip():
            signed.append((path, data))
    picked = random.Random(seed).sample(signed, min(n, len(signed)))
    lines = [
        "# 复核文件抽查清单",
        "",
        f"从 {len(signed)} 份已签字复核文件中按种子 {seed} 抽取 {len(picked)} 份。逐项打开来源，"
        "核对取值是否被原文支持；在「结果」处填「对」或「错（说明）」。",
    ]
    for path, data in sorted(picked, key=lambda x: x[0].stem):
        ticker = path.stem.upper()
        ids = {
            sid
            for part in ("clinical", "event", "rights")
            for sid in (data.get(part) or {}).get("sources", [])
        }
        sources = {
            s.source_id: s
            for s in session.exec(select(Source).where(col(Source.source_id).in_(ids))).all()
        }
        lines += ["", f"## {ticker}（`data/manual/reviews/{path.name}`）", ""]
        lines += [
            f"- 推荐方向：{data.get('program')} × {data.get('indication')} × {data.get('buyer')}",
        ]
        checks = [
            ("资产权益", (data.get("rights") or {}).get("status"), data.get("rights")),
            ("关键临床结果", (data.get("clinical") or {}).get("result"), data.get("clinical")),
            ("下一事件", (data.get("event") or {}).get("text"), data.get("event")),
        ]
        for label, value, part in checks:
            if not value:
                continue
            lines += [f"- **{label}**：{value}", "  - 来源："]
            for sid in (part or {}).get("sources", []):
                s = sources.get(sid)
                where = (s.url or s.local_path or "") if s else ""
                lines.append(f"    - `{sid}` {where}")
            lines.append("  - 结果：")
    return "\n".join(lines) + "\n"
