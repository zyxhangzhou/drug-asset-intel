"""Import the buyer workbook 《10家大型药企创新药资产偏好分析》.

Fact / inference follows the workbook's own 方法口径 sheet: signals and evidence are facts;
preferences, profiles, stages, deal forms and analysis are inferences.
"""

import json
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import openpyxl
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from intel.db import sha256_file
from intel.enums import ClaimKind, Confidence, LinkStatus, PreferenceDimension, SourceType
from intel.ingest import MATERIALS_RECEIVED_AT, BuildContext
from intel.models import Buyer, BuyerFinancial, BuyerPreference, BuyerProductLoe, MethodNote, Source

WORKBOOK_SOURCE_ID = "MNC-WB"
UNVERIFIED_MARK = "待核实"
EMPTY_MARKS = {"", "—", "-"}

CONFIDENCE = {
    "高": Confidence.high,
    "中高": Confidence.medium_high,
    "中": Confidence.medium,
    "低": Confidence.low,
}

BUYER_NAMES = {
    "MRK": "Merck & Co.",
    "BMY": "Bristol Myers Squibb",
    "PFE": "Pfizer",
    "NVS": "Novartis",
    "ABBV": "AbbVie",
    "JNJ": "Johnson & Johnson",
    "GSK": "GSK",
    "NVO": "Novo Nordisk",
    "ROG": "Roche",
    "AZN": "AstraZeneca",
}

# Short company names used in the overview sheet's LOE table.
LOE_ALIASES = {
    "Merck": "MRK",
    "BMS": "BMY",
    "Pfizer": "PFE",
    "Novartis": "NVS",
    "AbbVie": "ABBV",
    "J&J": "JNJ",
    "GSK": "GSK",
    "Novo": "NVO",
    "Roche": "ROG",
    "AZ": "AZN",
}

FACT, INFER = ClaimKind.fact, ClaimKind.inference

# (header, field, kind); field None = consumed elsewhere.
SUMMARY_COLUMNS = (
    ("公司", None, None),
    ("股票代码", None, None),
    ("最新财务与战略信号", "financial_signals", FACT),
    ("优先治疗领域（排序）", "therapeutic_priorities", INFER),
    ("优先技术类型（排序）", "modality_priorities", INFER),
    ("最可能交易阶段/形式", "deal_preference", INFER),
    ("购买动因", "buy_rationale", INFER),
    ("核心证据", "key_evidence", FACT),
    ("判断置信度", None, None),
    ("来源ID", None, None),
)

THERAPEUTIC_COLUMNS = (
    ("公司", None, None),
    ("优先级", None, None),
    ("治疗领域", "label", INFER),
    ("需求类型", "need_type", INFER),
    ("目标资产画像", "target_profile", INFER),
    ("事实证据", "evidence", FACT),
    ("分析推断", "analysis", INFER),
    ("理想阶段", "ideal_stage", INFER),
    ("来源ID", None, None),
)

MODALITY_COLUMNS = (
    ("公司", None, None),
    ("优先级", None, None),
    ("技术类型", "label", INFER),
    ("购买逻辑", "analysis", INFER),
    ("事实证据", "evidence", FACT),
    ("理想资产", "target_profile", INFER),
    ("建议交易形式", "deal_form", INFER),
    ("来源ID", None, None),
)

CAPACITY_COLUMNS = (
    ("公司", None),
    ("代码", None),
    ("币种", None),
    ("FY2025总收入(十亿)", "revenue_total"),
    ("FY2025美国收入(十亿)", "revenue_us"),
    ("美国占比", None),  # formula; derived by the app
    ("现金及短期投资(十亿)", "cash_and_short_term_investments"),
    ("总债务(十亿)", "total_debt"),
    ("净债务(十亿)", "net_debt"),
    ("自由现金流(十亿)", "free_cash_flow"),
    ("资本配置与火力备注", "capital_allocation_note"),
    ("已完成并购(2024–2026)", "recent_deals"),
    ("重点治疗领域", "focus_areas"),
    ("数据来源", None),
)

LOE_COLUMNS = (
    ("公司", None),
    ("产品", None),
    ("FY2025全球收入(十亿)", "revenue_global"),
    ("FY2025美国收入(十亿)", "revenue_us"),
    ("美国 LOE 时点", "us_loe"),
    ("仿制药/biosimilar 进展", "generic_status"),
    ("公司防御与对冲", "defense"),
    ("口径备注", "basis_note"),
)

NUMERIC_FIELDS = {
    "revenue_total",
    "revenue_us",
    "cash_and_short_term_investments",
    "total_debt",
    "net_debt",
    "free_cash_flow",
    "revenue_global",
}


class WorkbookLayoutError(ValueError):
    """The workbook no longer has the layout this importer was written against."""


# --- reading helpers ------------------------------------------------------------------


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text in EMPTY_MARKS else text


def _where(cell: Cell) -> str:
    return f"{cell.parent.title}!{cell.coordinate}"


def _check_header(ws: Worksheet, row: int, columns: tuple) -> None:
    actual = [_text(c.value) for c in ws[row][: len(columns)]]
    expected = [c[0] for c in columns]
    if actual != expected:
        raise WorkbookLayoutError(f"{ws.title} row {row}: expected {expected}, got {actual}")


def _source_ids(value: object) -> list[str]:
    return [s.strip() for s in re.split(r"[;；]", str(value or "")) if s.strip()]


def _data_rows(ws: Worksheet, header_row: int) -> Iterator[tuple[Cell, ...]]:
    for row in ws.iter_rows(min_row=header_row + 1):
        if _text(row[0].value) is None:
            return
        yield row


def _find_header(ws: Worksheet, first: str, second: str) -> int:
    for row in ws.iter_rows():
        if _text(row[0].value) == first and _text(row[1].value) == second:
            return row[0].row
    raise WorkbookLayoutError(f"{ws.title}: header {first}/{second} not found")


@dataclass(frozen=True)
class RegisterRow:
    source_id: str
    publisher: str | None
    doc_kind: str | None
    date_text: str | None
    title: str | None
    url: str | None
    note: str | None


def _date_text(value: object) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return _text(value)


def exact_date(text: str | None) -> date | None:
    """Only a full YYYY-MM-DD becomes a date; partial dates stay text."""
    if text and re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text)
    return None


def read_source_register(path: Path) -> list[RegisterRow]:
    ws = openpyxl.load_workbook(path, data_only=True)["来源登记"]
    header = ("来源ID", "公司", "资料类型", "资料日期", "标题", "官方/本地链接", "本研究使用的要点")
    _check_header(ws, 1, tuple((h,) for h in header))
    return [
        RegisterRow(
            source_id=_text(r[0].value),
            publisher=_text(r[1].value),
            doc_kind=_text(r[2].value),
            date_text=_date_text(r[3].value),
            title=_text(r[4].value),
            url=_text(r[5].value),
            note=_text(r[6].value),
        )
        for r in _data_rows(ws, 1)
    ]


# --- steps ----------------------------------------------------------------------------


def _register_sources(ctx: BuildContext) -> None:
    path = ctx.inputs.mnc_workbook
    ctx.session.add(
        Source(
            source_id=WORKBOOK_SOURCE_ID,
            source_type=SourceType.mnc_material,
            title=path.stem,
            doc_kind="对方提供的工作簿",
            fetched_at=MATERIALS_RECEIVED_AT,
            local_path=str(path),
            content_hash=sha256_file(path),
            link_status=LinkStatus.local_file,
        )
    )
    links = {}
    if ctx.inputs.link_results.exists():
        links = json.loads(ctx.inputs.link_results.read_text())
    else:
        ctx.notes.append("link check cache missing; MNC source links left unchecked")
    for row in read_source_register(path):
        checked = links.get(row.source_id)
        ctx.session.add(
            Source(
                source_id=row.source_id,
                source_type=SourceType.mnc_material,
                url=row.url,
                title=row.title,
                publisher=row.publisher,
                doc_kind=row.doc_kind,
                note=row.note,
                published_date_text=row.date_text,
                published_date=exact_date(row.date_text),
                fetched_at=MATERIALS_RECEIVED_AT,
                link_status=LinkStatus(checked["status"]) if checked else LinkStatus.unchecked,
                link_checked_at=datetime.fromisoformat(checked["checked_at"]) if checked else None,
            )
        )


def _claims_per_source(
    ctx: BuildContext,
    entity: str,
    obj,
    row: tuple[Cell, ...],
    columns: tuple,
    source_ids: list[str],
    confidence: Confidence,
    extra_note: str = "",
) -> None:
    for idx, (_, fld, kind) in enumerate(columns):
        if fld is None:
            continue
        value = getattr(obj, fld)
        if value is None:
            continue
        for sid in source_ids:
            ctx.claim(
                entity,
                obj.id,
                fld,
                value,
                sid,
                kind=kind,
                confidence=confidence if kind is INFER else None,
                note=f"对方材料 {_where(row[idx])}{extra_note}",
            )


def _import_summary(ctx: BuildContext, wb) -> dict[str, Buyer]:
    ws = wb["执行摘要"]
    _check_header(ws, 1, SUMMARY_COLUMNS)
    buyers = {}
    for row in _data_rows(ws, 1):
        ticker = _text(row[1].value)
        if ticker not in BUYER_NAMES:
            raise WorkbookLayoutError(f"unknown buyer ticker {ticker!r} at {_where(row[1])}")
        confidence = CONFIDENCE[_text(row[8].value)]
        buyer = Buyer(
            ticker=ticker,
            name=BUYER_NAMES[ticker],
            name_zh=_text(row[0].value),
            confidence=confidence,
        )
        for idx, (_, fld, _) in enumerate(SUMMARY_COLUMNS):
            if fld:
                setattr(buyer, fld, _text(row[idx].value))
        ctx.session.add(buyer)
        ctx.session.flush()
        _claims_per_source(
            ctx, "buyer", buyer, row, SUMMARY_COLUMNS, _source_ids(row[9].value), confidence
        )
        buyers[buyer.name_zh] = buyer
    return buyers


def _import_preferences(
    ctx: BuildContext, ws: Worksheet, columns: tuple, dimension: PreferenceDimension, buyers
) -> None:
    _check_header(ws, 1, columns)
    for row in _data_rows(ws, 1):
        buyer = buyers.get(_text(row[0].value))
        if buyer is None:
            raise WorkbookLayoutError(f"unknown buyer {row[0].value!r} at {_where(row[0])}")
        pref = BuyerPreference(
            buyer_id=buyer.id,
            dimension=dimension,
            rank=int(row[1].value),
            confidence=buyer.confidence,
        )
        for idx, (_, fld, _) in enumerate(columns):
            if fld:
                setattr(pref, fld, _text(row[idx].value))
        ctx.session.add(pref)
        ctx.session.flush()
        _claims_per_source(
            ctx,
            "buyer_preference",
            pref,
            row,
            columns,
            _source_ids(row[len(columns) - 1].value),
            buyer.confidence,
            extra_note="；置信度继承自执行摘要「判断置信度」",
        )


def _overview_value(ctx: BuildContext, entity: str, key: str, fld: str, cell: Cell):
    """Numbers flagged 待核实 become empty; text keeps its caveat but is listed as a gap."""
    text = _text(cell.value)
    if text is None:
        return None
    where = f"{_where(cell)}: {text}"
    if UNVERIFIED_MARK in text and (fld in NUMERIC_FIELDS or text == UNVERIFIED_MARK):
        ctx.gap(entity, key, fld, "unverified_in_material", where)
        return None
    if fld in NUMERIC_FIELDS:
        try:
            return float(text.replace(",", ""))
        except ValueError:
            ctx.gap(entity, key, fld, "non_numeric_in_material", where)
            return None
    if UNVERIFIED_MARK in text:
        ctx.gap(entity, key, fld, "partially_unverified_in_material", where)
    return text


def _import_overview_row(
    ctx: BuildContext, obj, entity: str, key: str, row, columns, note_suffix: str
) -> None:
    for idx, (_, fld) in enumerate(columns):
        if fld:
            setattr(obj, fld, _overview_value(ctx, entity, key, fld, row[idx]))
    ctx.session.add(obj)
    ctx.session.flush()
    for idx, (_, fld) in enumerate(columns):
        if fld and getattr(obj, fld) is not None:
            ctx.claim(
                entity,
                obj.id,
                fld,
                getattr(obj, fld),
                WORKBOOK_SOURCE_ID,
                note=f"对方材料 {_where(row[idx])}{note_suffix}{_caveat(getattr(obj, fld))}",
            )


def _caveat(value: object) -> str:
    return "；原文含「待核实」标记" if isinstance(value, str) and UNVERIFIED_MARK in value else ""


def _import_overview(ctx: BuildContext, wb, by_ticker: dict[str, Buyer]) -> None:
    ws = wb["MNC买方概览"]
    header = _find_header(ws, "公司", "代码")
    _check_header(ws, header, CAPACITY_COLUMNS)
    for row in _data_rows(ws, header):
        ticker = _text(row[1].value)
        if ticker not in by_ticker:
            raise WorkbookLayoutError(f"unknown buyer ticker {ticker!r} at {_where(row[1])}")
        fin = BuyerFinancial(
            buyer_id=by_ticker[ticker].id, fiscal_year="FY2025", currency=_text(row[2].value)
        )
        cited = _text(row[13].value)
        suffix = f"；原表数据来源：{cited}" if cited else ""
        _import_overview_row(ctx, fin, "buyer_financial", ticker, row, CAPACITY_COLUMNS, suffix)

    header = _find_header(ws, "公司", "产品")
    _check_header(ws, header, LOE_COLUMNS)
    for row in _data_rows(ws, header):
        name = _text(row[0].value)
        if name not in LOE_ALIASES:
            raise WorkbookLayoutError(f"unknown company {name!r} at {_where(row[0])}")
        ticker = LOE_ALIASES[name]
        product = _text(row[1].value)
        loe = BuyerProductLoe(buyer_id=by_ticker[ticker].id, product=product)
        key = f"{ticker}/{product}"
        _import_overview_row(ctx, loe, "buyer_product_loe", key, row, LOE_COLUMNS, "")

    for row in ws.iter_rows(min_row=header + 1):
        text = _text(row[0].value)
        if text and text.startswith("注"):
            ctx.session.add(
                MethodNote(source_id=WORKBOOK_SOURCE_ID, item="买方概览表注", text=text)
            )


def _import_method_notes(ctx: BuildContext, wb) -> None:
    ws = wb["方法口径"]
    _check_header(ws, 1, (("项目",), ("说明",)))
    for row in _data_rows(ws, 1):
        ctx.session.add(
            MethodNote(
                source_id=WORKBOOK_SOURCE_ID, item=_text(row[0].value), text=_text(row[1].value)
            )
        )


def ingest(ctx: BuildContext) -> None:
    _register_sources(ctx)
    ctx.session.flush()
    wb = openpyxl.load_workbook(ctx.inputs.mnc_workbook, data_only=True)
    buyers = _import_summary(ctx, wb)
    by_ticker = {b.ticker: b for b in buyers.values()}
    _import_preferences(
        ctx, wb["治疗领域分析"], THERAPEUTIC_COLUMNS, PreferenceDimension.therapeutic_area, buyers
    )
    _import_preferences(
        ctx, wb["技术类型分析"], MODALITY_COLUMNS, PreferenceDimension.modality, buyers
    )
    _import_overview(ctx, wb, by_ticker)
    _import_method_notes(ctx, wb)
