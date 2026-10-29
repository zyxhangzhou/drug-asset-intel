"""Index universe, ticker → CIK mapping, and verified Stage 0 exclusions."""

import csv
import json
from datetime import UTC, datetime

import openpyxl

from intel.db import sha256_file
from intel.enums import ClaimKind, Confidence, ExclusionCategory, LinkStatus, ProducedBy, SourceType
from intel.fetch import SEC_TICKERS_URL, read_fetched_at
from intel.ingest import MATERIALS_RECEIVED_AT, BuildContext
from intel.ingest.mnc import exact_date
from intel.models import Source, Target

INDEX_SOURCE_ID = "SPSIBI-WB"
SEC_TICKERS_SOURCE_ID = "SEC-TICKERS"

STAGE0_COLUMNS = (
    "ticker",
    "category",
    "reason",
    "kind",
    "confidence",
    "source_id",
    "source_type",
    "source_url",
    "source_title",
    "published_date",
    "accessed_on",
    "verified_by",
)


class Stage0FileError(ValueError):
    """The Stage 0 exclusion file is malformed."""


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper().replace(".", "-")


def _import_index(ctx: BuildContext) -> dict[str, Target]:
    path = ctx.inputs.index_workbook
    ctx.session.add(
        Source(
            source_id=INDEX_SOURCE_ID,
            source_type=SourceType.other,
            title=path.stem,
            doc_kind="对方提供的工作簿",
            fetched_at=MATERIALS_RECEIVED_AT,
            local_path=str(path),
            content_hash=sha256_file(path),
            link_status=LinkStatus.local_file,
        )
    )
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if [str(c).strip() for c in rows[0][:2]] != ["Ticker", "Company Name"]:
        raise ValueError(f"{path.name}: unexpected header {rows[0][:2]}")
    targets = {}
    for ticker, name, *_ in rows[1:]:
        if ticker is None:
            continue
        target = Target(ticker=str(ticker).strip(), name=str(name).strip())
        ctx.session.add(target)
        targets[target.ticker] = target
    ctx.session.flush()
    return targets


def _map_ciks(ctx: BuildContext, targets: dict[str, Target]) -> None:
    path = ctx.inputs.sec_tickers
    if not path.exists():
        for ticker in targets:
            ctx.gap("target", ticker, "cik", "sec_tickers_cache_missing", str(path))
        return
    ctx.session.add(
        Source(
            source_id=SEC_TICKERS_SOURCE_ID,
            source_type=SourceType.sec_filing,
            url=SEC_TICKERS_URL,
            title="SEC company_tickers.json",
            fetched_at=read_fetched_at(path) or datetime.fromtimestamp(path.stat().st_mtime, UTC),
            local_path=str(path),
            content_hash=sha256_file(path),
        )
    )
    ctx.session.flush()
    entries = {normalize_ticker(e["ticker"]): e for e in json.loads(path.read_text()).values()}
    for ticker, target in targets.items():
        entry = entries.get(normalize_ticker(ticker))
        if entry is None:
            ctx.gap("target", ticker, "cik", "ticker_not_in_sec_file", SEC_TICKERS_URL)
            continue
        target.cik = f"{int(entry['cik_str']):010d}"
        ctx.claim(
            "target",
            target.id,
            "cik",
            target.cik,
            SEC_TICKERS_SOURCE_ID,
            produced_by=ProducedBy.api,
            note=f"SEC title: {entry['title']}",
        )


def _read_stage0(ctx: BuildContext) -> list[dict[str, str]]:
    path = ctx.inputs.stage0_exclusions
    if not path.exists():
        ctx.notes.append(f"no Stage 0 file at {path}; no exclusions applied")
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != STAGE0_COLUMNS:
            raise Stage0FileError(f"{path}: columns must be {list(STAGE0_COLUMNS)}")
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _apply_stage0(ctx: BuildContext, targets: dict[str, Target]) -> None:
    rows = _read_stage0(ctx)
    pending = [r for r in rows if not r["verified_by"]]
    if pending:
        tickers = ", ".join(r["ticker"] for r in pending)
        ctx.notes.append(f"{len(pending)} unverified Stage 0 row(s) not applied: {tickers}")
    for row in (r for r in rows if r["verified_by"]):
        target = targets.get(row["ticker"])
        if target is None:
            raise Stage0FileError(f"Stage 0 ticker {row['ticker']!r} is not in the index")
        with ctx.session.no_autoflush:
            known = ctx.session.get(Source, row["source_id"])
        if known is None:
            ctx.session.add(
                Source(
                    source_id=row["source_id"],
                    source_type=SourceType(row["source_type"]),
                    url=row["source_url"],
                    title=row["source_title"] or None,
                    published_date_text=row["published_date"] or None,
                    published_date=exact_date(row["published_date"]),
                    fetched_at=datetime.fromisoformat(row["accessed_on"]).replace(tzinfo=UTC),
                )
            )
            ctx.session.flush()
        kind = ClaimKind(row["kind"])
        target.excluded = True
        target.exclusion_category = ExclusionCategory(row["category"])
        target.exclusion_reason = row["reason"]
        ctx.claim(
            "target",
            target.id,
            "exclusion_reason",
            row["reason"],
            row["source_id"],
            kind=kind,
            confidence=Confidence(row["confidence"]) if row["confidence"] else None,
            note=f"Stage 0 {row['category']}；核实人 {row['verified_by']}",
        )


def ingest(ctx: BuildContext) -> None:
    targets = _import_index(ctx)
    _map_ciks(ctx, targets)
    _apply_stage0(ctx, targets)
