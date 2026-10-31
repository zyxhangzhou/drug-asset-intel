"""《候选生物制药公司列表》Excel, read from the snapshot only.

Every key value sits next to a source column ("ID（事实）; ID（推断·中）"); the 来源 sheet lists
every cited source. Cell contents depend only on the snapshot, so one snapshot always exports the
same workbook contents.
"""

import csv
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from sqlmodel import Session, col, select

from intel import views
from intel.models import (
    Catalyst,
    FinancialSnapshot,
    Program,
    Recommendation,
    SnapshotMeta,
    Source,
    Target,
    Trial,
    TrialResult,
)
from intel.scoring import DIMENSIONS

FILE_NAME = "候选生物制药公司列表.xlsx"
CATALYST_WINDOW_DAYS = 730  # the brief's 12–24 months, counted from the snapshot date
MILLION = 1_000_000

STAGE = {
    "preclinical": "临床前",
    "phase1": "1 期",
    "phase1_2": "1/2 期",
    "phase2": "2 期",
    "phase2_3": "2/3 期",
    "phase3": "3 期",
    "filed": "已申报",
    "approved": "已上市",
    "unknown": "未知",
}
TA = {
    "oncology": "肿瘤",
    "heme_malignancy": "血液肿瘤",
    "hematology": "血液（非肿瘤）",
    "immunology": "免疫",
    "neuroscience": "神经",
    "infectious": "感染",
    "rare_genetic": "罕见遗传病",
    "obesity_metabolic": "肥胖与代谢",
    "cardiovascular": "心血管",
    "respiratory": "呼吸",
    "ophthalmology": "眼科",
    "liver": "肝病",
    "renal": "肾病",
    "attr": "ATTR 淀粉样变",
}
LATE_STAGES = {"phase2", "phase2_3", "phase3", "filed"}
STATUS = {"deep": "深度研究", "reviewed": "已复核", "auto": "自动初筛"}
RIGHTS = {"full": "全部权益", "partial": "部分地区已授出", "restricted": "受限"}
CONFIDENCE = {"high": "高", "medium_high": "中高", "medium": "中", "low": "低"}
KIND = {"fact": "事实", "inference": "推断"}
DATE_TYPE = {"ESTIMATED": "预计", "ACTUAL": "实际"}
DIMENSION_LABELS = {
    "buyer_fit": "买方契合度",
    "stage_match": "研发阶段匹配度",
    "clinical": "临床证据与差异化",
    "catalyst": "近期催化",
    "dealability": "可交易性",
}


class Cited:
    """Collects every source ID written into a source column, for the 来源 sheet."""

    def __init__(self) -> None:
        self.ids: set[str] = set()

    def __call__(self, sources: views.Sources, *fields: str) -> str:
        seen: dict[str, str] = {}
        for f in fields:
            for c in sources.get(f, []):
                tag = KIND[c.kind]
                if c.kind == "inference" and c.confidence:
                    tag += "·" + CONFIDENCE[c.confidence]
                if c.produced_by == "llm":
                    tag += "·LLM"
                sid = c.source.source_id
                seen.setdefault(sid, f"{sid}（{tag}）")
        self.ids.update(seen)
        return "; ".join(seen.values())


def _m(value: float | None) -> float | None:
    return None if value is None else round(value / MILLION, 1)


def _ta(codes: str | None) -> str:
    return "、".join(TA.get(c, c) for c in codes.split(";")) if codes else "未归类"


def _csv(path: Path | None) -> list[dict[str, str]]:
    if not path or not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def export(db_session: Session, out: Path, outputs_dir: Path | None = None) -> Path:
    """Write the workbook; `outputs_dir` holds the build's gaps.csv and longlist.csv."""
    cite = Cited()
    meta = db_session.get(SnapshotMeta, 1)
    snapshot = meta.snapshot_date if meta else None
    wb = Workbook()
    wb.remove(wb.active)
    longlist = _csv(outputs_dir / "longlist.csv" if outputs_dir else None)
    reasons = {row["ticker"]: row["not_shortlisted_reason"] for row in longlist}
    status_counts = _companies(wb, db_session, cite, reasons)
    _pipeline(wb, db_session, cite)
    _clinical(wb, db_session, cite)
    _catalysts(wb, db_session, cite, snapshot)
    _sources(wb, db_session, cite.ids)
    _gaps(wb, _csv(outputs_dir / "gaps.csv" if outputs_dir else None))
    _readme(wb, meta, status_counts)
    wb.move_sheet("说明", offset=-(len(wb.sheetnames) - 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def _sheet(wb: Workbook, title: str, header: list[tuple[str, int]], rows: Iterable[list]) -> None:
    ws = wb.create_sheet(title)
    ws.append([h for h, _ in header])
    for i, (_, width) in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    for row in rows:
        ws.append(row)
    wrap = Alignment(wrap_text=True, vertical="top")
    for line in ws.iter_rows(min_row=2):
        for cell in line:
            cell.alignment = wrap
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions


def _companies(wb: Workbook, s: Session, cite: Cited, reasons: dict[str, str]) -> dict[str, int]:
    recs = s.exec(select(Recommendation).where(Recommendation.is_primary)).all()
    outs = views._recommendations(s, list(recs))
    fins = {
        f.target_id: f
        for f in s.exec(select(FinancialSnapshot).order_by(col(FinancialSnapshot.as_of))).all()
    }
    fin_src = views.claims_by_entity(s, "financial_snapshot", (f.id for f in fins.values()))
    rows, counts = [], dict.fromkeys(STATUS, 0)
    order = sorted(
        zip(recs, outs, strict=True), key=lambda x: (-x[1].conservative, x[0].target.ticker)
    )
    for rank, (rec, o) in enumerate(order, 1):
        t: Target = rec.target
        f = fins.get(t.id)
        fs = fin_src.get(f.id, {}) if f else {}
        counts[o.research_status] += 1
        rows.append(
            [
                rank,
                t.ticker,
                t.name,
                t.cik,
                STATUS[o.research_status],
                "是" if t.shortlisted else "",
                o.thesis,
                cite(o.sources, "thesis"),
                None if t.shortlisted else reasons.get(t.ticker),
                o.asset,
                o.indication,
                _ta(o.therapeutic_area),
                STAGE.get(o.stage or "unknown"),
                o.buyer,
                o.preference,
                *[o.scores[d] for d in DIMENSIONS],
                o.conservative,
                o.optimistic,
                round(o.coverage * 100),
                f.as_of.isoformat() if f else None,
                _m(f.market_cap) if f else None,
                cite(fs, "market_cap", "share_price", "shares_outstanding"),
                _m(f.cash_and_investments) if f else None,
                cite(fs, "cash_and_investments"),
                _m(f.total_debt) if f else None,
                cite(fs, "total_debt"),
                round(f.runway_months, 1) if f and f.runway_months is not None else None,
                cite(fs, "runway_months", "operating_cash_flow_ytd"),
                _m(o.enterprise_value),
                cite(o.sources, "enterprise_value"),
                _m(f.acquisition_cost_low) if f else None,
                _m(f.acquisition_cost_high) if f else None,
                cite(fs, "acquisition_cost_low", "acquisition_cost_high"),
                RIGHTS.get(o.rights_status or "", "待核实"),
                cite(o.sources, "rights_status"),
                o.next_event,
                o.event_timing,
                cite(o.sources, "next_event", "event_timing"),
            ]
        )
    _sheet(
        wb,
        "候选公司",
        [
            ("排名（保守分）", 8),
            ("代码", 8),
            ("公司", 26),
            ("CIK", 11),
            ("研究状态", 9),
            ("入选", 6),
            ("推荐逻辑（入选理由）", 60),
            ("推荐逻辑来源", 24),
            ("未入选原因", 20),
            ("主推荐资产", 22),
            ("适应症", 26),
            ("治疗领域", 14),
            ("研发阶段", 9),
            ("主要买方", 16),
            ("对应偏好", 18),
            *[(DIMENSION_LABELS[d] + "（0–4）", 9) for d in DIMENSIONS],
            ("保守分", 8),
            ("乐观分", 8),
            ("证据覆盖率（%）", 8),
            ("财务截至", 11),
            ("市值（百万美元）", 11),
            ("市值来源", 24),
            ("现金及投资（百万美元）", 11),
            ("现金来源", 22),
            ("总债务（百万美元）", 11),
            ("债务来源", 22),
            ("资金可支撑月数", 9),
            ("可支撑月数来源", 22),
            ("企业价值（百万美元）", 11),
            ("企业价值来源", 24),
            ("收购成本下限（百万美元）", 11),
            ("收购成本上限（百万美元）", 11),
            ("收购成本来源", 26),
            ("资产权益", 10),
            ("资产权益来源", 22),
            ("下一事件", 40),
            ("事件时间", 10),
            ("下一事件来源", 24),
        ],
        rows,
    )
    return counts


def _pipeline(wb: Workbook, s: Session, cite: Cited) -> None:
    programs = s.exec(select(Program).order_by(col(Program.target_id), col(Program.name))).all()
    psrc = views.claims_by_entity(s, "program", (p.id for p in programs))
    pis = [pi for p in programs for pi in p.indications]
    isrc = views.claims_by_entity(s, "program_indication", (pi.id for pi in pis))
    rows = []
    for p in programs:
        ps = psrc.get(p.id, {})
        for pi in p.indications or [None]:
            si = isrc.get(pi.id, {}) if pi else {}
            rows.append(
                [
                    p.target.ticker,
                    p.target.name,
                    p.name,
                    p.mechanism,
                    cite(ps, "mechanism"),
                    p.modality,
                    cite(ps, "modality"),
                    pi.indication if pi else None,
                    _ta(pi.therapeutic_area) if pi else None,
                    STAGE.get(pi.stage) if pi else None,
                    cite(si, "indication", "therapeutic_area", "stage"),
                ]
            )
    _sheet(
        wb,
        "管线",
        [
            ("代码", 8),
            ("公司", 26),
            ("药物", 26),
            ("作用机制", 40),
            ("作用机制来源", 24),
            ("技术类型", 16),
            ("技术类型来源", 22),
            ("适应症", 30),
            ("治疗领域", 14),
            ("研发阶段", 9),
            ("适应症与阶段来源", 30),
        ],
        rows,
    )


def _clinical(wb: Workbook, s: Session, cite: Cited) -> None:
    rows = []
    reviewed = s.exec(
        select(Recommendation).where(
            Recommendation.is_primary, col(Recommendation.result).is_not(None)
        )
    ).all()
    for rec, o in zip(reviewed, views._recommendations(s, list(reviewed)), strict=True):
        rows.append(
            [
                rec.target.ticker,
                rec.target.name,
                "复核结论",
                o.asset,
                None,
                o.indication,
                o.design,
                o.result,
                None,
                o.comparability,
                o.limitation,
                cite(o.sources, "design", "result", "comparability", "limitation"),
            ]
        )
    results = s.exec(
        select(TrialResult).order_by(col(TrialResult.trial_id), col(TrialResult.id))
    ).all()
    rsrc = views.claims_by_entity(s, "trial_result", (r.id for r in results))
    for r in results:
        trial: Trial = r.trial
        rows.append(
            [
                trial.target.ticker,
                trial.target.name,
                "试验结果",
                trial.title,
                trial.nct_id,
                r.endpoint,
                None,
                r.result,
                r.analysis,
                r.comparator,
                r.advantage_vs_soc,
                cite(
                    rsrc.get(r.id, {}),
                    "endpoint",
                    "result",
                    "analysis",
                    "comparator",
                    "advantage_vs_soc",
                ),
            ]
        )
    rows.sort(key=lambda x: (x[0], x[2] != "复核结论"))
    _sheet(
        wb,
        "临床数据",
        [
            ("代码", 8),
            ("公司", 26),
            ("类型", 9),
            ("资产 / 试验标题", 34),
            ("NCT", 13),
            ("适应症 / 终点", 34),
            ("研究设计", 40),
            ("结果", 50),
            ("统计分析", 30),
            ("对照 / 可比性", 34),
            ("相对标准治疗的优势 / 局限", 40),
            ("来源", 30),
        ],
        rows,
    )


def _catalysts(wb: Workbook, s: Session, cite: Cited, snapshot: date | None) -> None:
    rows = []
    cats = s.exec(select(Catalyst)).all()
    csrc = views.claims_by_entity(s, "catalyst", (c.id for c in cats))
    for c in cats:
        window = f"{c.window_start or '?'} – {c.window_end or '?'}"
        rows.append(
            [
                c.target.ticker,
                c.target.name,
                c.event,
                None,
                window,
                "公司披露",
                cite(csrc.get(c.id, {}), "event", "window_start", "window_end"),
            ]
        )
    recs = s.exec(
        select(Recommendation).where(
            Recommendation.is_primary, col(Recommendation.next_event).is_not(None)
        )
    ).all()
    for rec, o in zip(recs, views._recommendations(s, list(recs)), strict=True):
        rows.append(
            [
                rec.target.ticker,
                rec.target.name,
                o.next_event,
                o.asset,
                o.event_timing,
                "推荐方向的下一事件",
                cite(o.sources, "next_event", "event_timing"),
            ]
        )
    if snapshot:
        end = (snapshot + timedelta(days=CATALYST_WINDOW_DAYS)).isoformat()
        trials = s.exec(
            select(Trial).where(
                col(Trial.indication_id).is_not(None),
                col(Trial.primary_completion_date) >= snapshot.isoformat(),
                col(Trial.primary_completion_date) <= end,
            )
        ).all()
        trials = [t for t in trials if t.phase in LATE_STAGES]
        tsrc = views.claims_by_entity(s, "trial", (t.id for t in trials))
        for t in trials:
            kind = DATE_TYPE.get(t.primary_completion_type or "", "")
            rows.append(
                [
                    t.target.ticker,
                    t.target.name,
                    f"{t.nct_id} 主要完成（{STAGE.get(t.phase)}）：{t.title}",
                    t.indication.program.name if t.indication else None,
                    f"{t.primary_completion_date}（{kind}）",
                    "CT.gov 预计主要完成日（推断）",
                    cite(tsrc.get(t.id, {}), "primary_completion_date"),
                ]
            )
    rows.sort(key=lambda x: (x[0], x[5], str(x[4])))
    _sheet(
        wb,
        "催化事件",
        [
            ("代码", 8),
            ("公司", 26),
            ("事件", 60),
            ("药物", 22),
            ("时间", 22),
            ("出处", 22),
            ("来源", 30),
        ],
        rows,
    )


def _sources(wb: Workbook, s: Session, ids: set[str]) -> None:
    sources = s.exec(
        select(Source).where(col(Source.source_id).in_(ids)).order_by(col(Source.source_id))
    ).all()
    rows = [
        [
            x.source_id,
            x.title,
            x.source_type,
            x.publisher,
            x.published_date.isoformat() if x.published_date else x.published_date_text,
            x.fetched_at.date().isoformat(),
            x.url,
        ]
        for x in sources
    ]
    _sheet(
        wb,
        "来源",
        [
            ("来源 ID", 30),
            ("标题", 50),
            ("类型", 14),
            ("发布者", 24),
            ("发布日期", 12),
            ("抓取 / 访问日期", 12),
            ("网址", 60),
        ],
        rows,
    )


def _gaps(wb: Workbook, gaps: list[dict[str, str]]) -> None:
    rows = [list(r.values()) for r in gaps]
    _sheet(wb, "缺口", [("实体", 18), ("键", 16), ("字段", 22), ("原因", 22), ("说明", 70)], rows)


# 说明 sheet: (label, text). Short rows, one point each; counts and dates are filled in at export.
README = [
    ("文件", "《候选生物制药公司列表》"),
    ("范围", "10 家大型药企的资产偏好 × 标普生物科技指数成分公司"),
    ("数据截至（快照日）", "{snapshot_date}"),
    ("快照生成时间", "{generated_at}"),
    ("生成程序", "{generator}"),
    ("", ""),
    ("候选公司", "每家公司一行，按主推荐方向的保守分排序（题面第二部分 1、6 项）"),
    ("", "主推荐方向 = 资产 × 适应症 × 买方；公司分数按它计算"),
    ("管线", "药物、作用机制、适应症与研发阶段（第 2、3 项）"),
    ("临床数据", "复核结论与试验结果，含相对标准治疗的优势（第 4 项）"),
    ("催化事件", "快照日起 24 个月内的事件（第 5 项）"),
    ("", "出处分三种：公司披露、推荐方向的下一事件、CT.gov 预计主要完成日"),
    ("来源", "本文件引用的全部来源，含发布日期与抓取时间（第 7 项）"),
    ("缺口", "找不到来源而留空的字段"),
    ("", ""),
    ("来源列", "「来源 ID（事实）」：来源原文直接支持"),
    ("", "「来源 ID（推断·中）」：分析判断，后缀为置信度"),
    ("", "「·LLM」：经签字复核的模型抽取，原文片段已校验"),
    ("金额单位", "百万美元"),
    ("空白", "没有来源支持的值；不是零，也不是估算"),
    ("收购成本", "企业价值 + 市值 × 收购溢价区间，为推断"),
    ("", "只对深度研究公司填写；方法与来源见收购成本来源列"),
    ("", ""),
    ("完成情况", "按研究状态："),
    ("深度研究 {deep} 家", "复核全部字段，另核对临床数据、催化事件，并估算收购成本"),
    ("已复核 {reviewed} 家", "人工复核推荐方向、五维分数、资产权益、下一事件与推荐逻辑"),
    ("自动初筛 {auto} 家", "结构化字段自动填充，五维分数按规则计算；未人工复核，不入选"),
]


def _readme(wb: Workbook, meta: SnapshotMeta | None, counts: dict[str, int]) -> None:
    ws = wb.create_sheet("说明")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 80
    values = {
        **counts,
        "snapshot_date": meta.snapshot_date.isoformat() if meta and meta.snapshot_date else "未知",
        "generated_at": meta.generated_at.isoformat() if meta else "未知",
        "generator": meta.generator if meta else "未知",
    }
    for label, text in README:
        ws.append([label.format(**values), text.format(**values)])
    for row in ws.iter_rows():
        row[0].font = Font(bold=True)
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
