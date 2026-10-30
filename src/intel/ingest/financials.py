"""Financial snapshot per candidate: SEC XBRL values, Nasdaq close, market cap and runway.

Filed values are facts sourced to their filing. The price is a fact from an unofficial source.
Market cap is arithmetic on two facts and cites both. Runway is a projection, so an inference.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlmodel import select

from intel.config import Settings
from intel.enums import ClaimKind, Confidence, ProducedBy, SourceType
from intel.fetch import (
    SEC_DELAY,
    Throttled,
    read_fetched_at,
    request_record,
    run_batch,
    sec_headers,
    write_cache,
)
from intel.ingest import SNAPSHOT_DATE, BuildContext, Inputs
from intel.ingest.pool import Company, candidate_pool
from intel.models import FinancialSnapshot, Source, Target

COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
FILING_INDEX = "https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{accn}-index.html"
NASDAQ_HISTORY = "https://api.nasdaq.com/api/quote/{ticker}/historical"
NASDAQ_PAGE = "https://www.nasdaq.com/market-activity/stocks/{ticker}/historical"
BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

CASH_COMBINED = (
    "CashCashEquivalentsAndShortTermInvestments",
    "CashCashEquivalentsAndMarketableSecuritiesCurrent",
)
CASH = "CashAndCashEquivalentsAtCarryingValue"
# Some filers (ARWR since 2024) tag only the cash-flow statement total, which includes a usually
# small restricted-cash amount; used only when CASH is not filed for the period.
CASH_WITH_RESTRICTED = "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
INVEST_CURRENT = (
    "ShortTermInvestments",
    "MarketableSecuritiesCurrent",
    "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
    "DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent",
    "AvailableForSaleSecuritiesCurrent",
    "HeldToMaturitySecuritiesCurrent",
)
INVEST_NONCURRENT = (
    "MarketableSecuritiesNoncurrent",
    "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
    "DebtSecuritiesAvailableForSaleExcludingAccruedInterestNoncurrent",
    "HeldToMaturitySecuritiesNoncurrent",
    "LongTermInvestments",
)
# Unclassified totals; used only when no current / noncurrent split is filed.
INVEST_TOTAL = (
    "AvailableForSaleSecuritiesDebtSecurities",
    "DebtSecuritiesAvailableForSaleExcludingAccruedInterest",
    "MarketableSecurities",
    "Investments",
)
DEBT_TOTAL = ("LongTermDebt",)
DEBT_SPLIT = ("LongTermDebtNoncurrent", "LongTermDebtCurrent")
# Single-tag fallbacks, first hit wins: filers that never tag LongTermDebt use one of these.
DEBT_SINGLE = (
    "ConvertibleNotesPayable",
    "ConvertibleDebtNoncurrent",
    "ConvertibleLongTermNotesPayable",
    "LongTermNotesPayable",
    "LongTermLoansPayable",
    "SecuredLongTermDebt",
    "NotesPayable",
    "LoansPayable",
)
OCF = "NetCashProvidedByUsedInOperatingActivities"
SHARES = "EntityCommonStockSharesOutstanding"  # dei, cover page
BALANCE_SHARES = "CommonStockSharesOutstanding"  # us-gaap, balance sheet
STALE_SHARES_DAYS = 120
US_GAAP_TAGS = {
    *CASH_COMBINED,
    CASH,
    CASH_WITH_RESTRICTED,
    *INVEST_CURRENT,
    *INVEST_NONCURRENT,
    *INVEST_TOTAL,
    *DEBT_TOTAL,
    *DEBT_SPLIT,
    *DEBT_SINGLE,
    OCF,
    BALANCE_SHARES,
}
FORMS = {"10-K", "10-Q"}
RUNWAY_NOTE = "资金可支撑月数 = 现金及投资 ÷ 月均经营现金消耗（−经营现金流 ÷ 期间月数）；推算值"


def xbrl_cache(inputs: Inputs, cik: str) -> Path:
    return inputs.raw_dir / "sec" / "companyfacts" / f"{cik}.json"


def price_cache(inputs: Inputs, ticker: str) -> Path:
    return inputs.raw_dir / "nasdaq" / f"{ticker}.json"


# --- fetch ----------------------------------------------------------------------------


def trim_companyfacts(body: dict) -> dict:
    facts = body.get("facts", {})
    gaap = facts.get("us-gaap", {})
    return {
        "cik": body.get("cik"),
        "entityName": body.get("entityName"),
        "taxonomies": sorted(facts),
        "us-gaap": {t: gaap[t]["units"] for t in sorted(US_GAAP_TAGS) if t in gaap},
        "dei": {t: facts["dei"][t]["units"] for t in (SHARES,) if t in facts.get("dei", {})},
    }


def fetch_xbrl(
    inputs: Inputs, http: Throttled, companies: list[Company], settings: Settings, refresh=False
):
    headers = sec_headers(settings)
    with_cik = [c for c in companies if c.cik]

    def one(company: Company) -> None:
        resp = http.get(COMPANYFACTS_URL.format(cik=company.cik), headers=headers)
        resp.raise_for_status()
        write_cache(
            xbrl_cache(inputs, company.cik), trim_companyfacts(resp.json()), [request_record(resp)]
        )

    http.delay = max(http.delay, SEC_DELAY)
    return run_batch(with_cik, lambda c: xbrl_cache(inputs, c.cik), one, refresh)


def fetch_prices(inputs: Inputs, http: Throttled, companies: list[Company], refresh=False):
    params = {
        "assetclass": "stocks",
        "fromdate": (SNAPSHOT_DATE - timedelta(days=14)).isoformat(),
        "todate": SNAPSHOT_DATE.isoformat(),
        "limit": 20,
    }

    def one(company: Company) -> None:
        resp = http.get(
            NASDAQ_HISTORY.format(ticker=company.ticker), params=params, headers=BROWSER_HEADERS
        )
        resp.raise_for_status()
        body = resp.json()
        rows = ((body.get("data") or {}).get("tradesTable") or {}).get("rows")
        if not rows:
            raise ValueError(f"no price rows: {body.get('status')}")
        write_cache(price_cache(inputs, company.ticker), {"rows": rows}, [request_record(resp)])

    return run_batch(companies, lambda c: price_cache(inputs, c.ticker), one, refresh)


# --- XBRL selection -------------------------------------------------------------------


@dataclass(frozen=True)
class Fact:
    tag: str
    value: float
    end: date
    start: date | None
    accn: str
    form: str
    filed: date


def _facts(units: dict, tag: str, unit: str) -> list[Fact]:
    out = []
    for e in units.get(tag, {}).get(unit, []):
        filed = date.fromisoformat(e["filed"])
        if e.get("form") not in FORMS or filed > SNAPSHOT_DATE:
            continue
        out.append(
            Fact(
                tag=tag,
                value=float(e["val"]),
                end=date.fromisoformat(e["end"]),
                start=date.fromisoformat(e["start"]) if e.get("start") else None,
                accn=e["accn"],
                form=e["form"],
                filed=filed,
            )
        )
    return out


def _at(facts: list[Fact], end: date) -> Fact | None:
    """The instant value at `end`, as last filed (restatements win)."""
    hits = [f for f in facts if f.end == end and f.start is None]
    return max(hits, key=lambda f: f.filed) if hits else None


def _first_at(gaap: dict, tags: tuple[str, ...], end: date) -> Fact | None:
    for tag in tags:
        fact = _at(_facts(gaap, tag, "USD"), end)
        if fact:
            return fact
    return None


def _anchor(gaap: dict) -> date | None:
    ends = [
        f.end
        for tag in (*CASH_COMBINED, CASH, CASH_WITH_RESTRICTED)
        for f in _facts(gaap, tag, "USD")
        if f.start is None
    ]
    return max(ends) if ends else None


def cash_and_investments(gaap: dict, end: date) -> list[Fact]:
    combined = _first_at(gaap, CASH_COMBINED, end)
    if combined:
        return [combined]  # never add a combined tag to its components
    split = [_first_at(gaap, INVEST_CURRENT, end), _first_at(gaap, INVEST_NONCURRENT, end)]
    investments = [p for p in split if p] or [_first_at(gaap, INVEST_TOTAL, end)]
    return [p for p in (_first_at(gaap, (CASH, CASH_WITH_RESTRICTED), end), *investments) if p]


def total_debt(gaap: dict, end: date) -> list[Fact]:
    for group in ((DEBT_TOTAL[0],), DEBT_SPLIT):
        parts = [p for p in (_first_at(gaap, (t,), end) for t in group) if p]
        if parts:
            return parts
    single = _first_at(gaap, DEBT_SINGLE, end)
    return [single] if single else []


def operating_cash_flow(gaap: dict, end: date) -> Fact | None:
    """The year-to-date figure ending at `end` (the longest period up to twelve months)."""
    hits = [
        f
        for f in _facts(gaap, OCF, "USD")
        if f.end == end and f.start and (f.end - f.start).days <= 370
    ]
    if not hits:
        return None
    return max(hits, key=lambda f: ((f.end - f.start).days, f.filed))


def full_year_operating_cash_flow(gaap: dict, end: date) -> Fact | None:
    """The latest fiscal-year figure ending on or before `end` and less than 15 months old."""
    hits = [
        f
        for f in _facts(gaap, OCF, "USD")
        if f.start and 350 <= (f.end - f.start).days <= 370 and 0 <= (end - f.end).days <= 460
    ]
    return max(hits, key=lambda f: (f.end, f.filed)) if hits else None


def burn_basis(ytd: Fact | None, year: Fact | None) -> Fact | None:
    """The period with the higher monthly cash burn, or None when neither burns cash.

    A one-off inflow (a licence upfront) can make a year-to-date figure look nearly
    self-funding; taking the worse of year-to-date and last fiscal year keeps the runway
    a conservative estimate.
    """
    burning = [f for f in (ytd, year) if f and f.value < 0]
    return max(burning, key=lambda f: -f.value / months(f)) if burning else None


def months(fact: Fact) -> int:
    return round((fact.end - fact.start).days / 30.44)


def shares_outstanding(dei: dict, gaap: dict) -> Fact | None:
    """The most recent of the cover-page count and the balance-sheet count.

    Some filers stop tagging the cover-page count; its last value can be years old.
    """
    facts = _facts(dei, SHARES, "shares") + [
        f for f in _facts(gaap, BALANCE_SHARES, "shares") if f.start is None
    ]
    return max(facts, key=lambda f: (f.end, f.filed)) if facts else None


# --- build ----------------------------------------------------------------------------


def _filing_source(ctx: BuildContext, fact: Fact, cik: str, path: Path) -> str:
    source_id = f"SEC-{fact.accn}"
    if ctx.session.get(Source, source_id) is None:
        ctx.session.add(
            Source(
                source_id=source_id,
                source_type=SourceType.sec_xbrl,
                url=FILING_INDEX.format(
                    cik=int(cik), folder=fact.accn.replace("-", ""), accn=fact.accn
                ),
                title=f"{fact.form} filed {fact.filed.isoformat()} (accession {fact.accn})",
                doc_kind=f"SEC {fact.form}（XBRL）",
                published_date=fact.filed,
                published_date_text=fact.filed.isoformat(),
                fetched_at=read_fetched_at(path),
                local_path=str(path),
            )
        )
        ctx.session.flush()
    return source_id


def _fact_note(facts: list[Fact]) -> str:
    tags = " + ".join(f.tag for f in facts)
    f = facts[0]
    return f"XBRL {tags}；期间结束 {f.end}；{f.form} 申报于 {f.filed}"


def _price(ctx: BuildContext, company: Company) -> tuple[float, date, str] | None:
    path = price_cache(ctx.inputs, company.ticker)
    if not path.exists():
        ctx.gap(
            "financial_snapshot", company.ticker, "share_price", "price_cache_missing", str(path)
        )
        return None
    rows = []
    for row in json.loads(path.read_text())["rows"]:
        day = datetime.strptime(row["date"], "%m/%d/%Y").date()
        if day <= SNAPSHOT_DATE:
            rows.append((day, float(row["close"].replace("$", "").replace(",", ""))))
    if not rows:
        ctx.gap("financial_snapshot", company.ticker, "share_price", "no_close_by_snapshot", "")
        return None
    day, close = max(rows)
    source_id = f"NASDAQ-{company.ticker}-{day.isoformat()}"
    ctx.session.add(
        Source(
            source_id=source_id,
            source_type=SourceType.market_data,
            url=NASDAQ_PAGE.format(ticker=company.ticker.lower()),
            title=f"Nasdaq historical quotes {company.ticker}",
            doc_kind="非官方行情（Nasdaq 网站接口）",
            published_date=day,
            published_date_text=day.isoformat(),
            fetched_at=read_fetched_at(path),
            local_path=str(path),
        )
    )
    ctx.session.flush()
    return close, day, source_id


def _snapshot_for(ctx: BuildContext, company: Company, target: Target) -> None:
    path = xbrl_cache(ctx.inputs, company.cik) if company.cik else None
    if path is None or not path.exists():
        reason = "no_cik" if path is None else "xbrl_cache_missing"
        ctx.gap("financial_snapshot", company.ticker, "*", reason, str(path or ""))
        return
    data = json.loads(path.read_text())
    gaap, dei = data["us-gaap"], data["dei"]
    end = _anchor(gaap) if "us-gaap" in data["taxonomies"] else None
    if end is None:
        reason = "no_us_gaap_balance_sheet" if "us-gaap" in data["taxonomies"] else "no_us_gaap"
        ctx.gap(
            "financial_snapshot", company.ticker, "*", reason, f"taxonomies: {data['taxonomies']}"
        )
        return

    snap = FinancialSnapshot(target_id=target.id, as_of=end)
    ctx.session.add(snap)
    ctx.session.flush()

    def record(fld: str, value, facts: list[Fact], note: str | None = None) -> None:
        setattr(snap, fld, value)
        for accn in dict.fromkeys(f.accn for f in facts):
            used = [f for f in facts if f.accn == accn]
            ctx.claim(
                "financial_snapshot",
                snap.id,
                fld,
                value,
                _filing_source(ctx, used[0], company.cik, path),
                produced_by=ProducedBy.api,
                as_of=used[0].end,
                note=note or _fact_note(used),
            )

    cash = cash_and_investments(gaap, end)
    if cash:
        record("cash_and_investments", sum(f.value for f in cash), cash)
    else:
        ctx.gap(
            "financial_snapshot", company.ticker, "cash_and_investments", "no_cash_tag", str(end)
        )
    debt = total_debt(gaap, end)
    if debt:
        record("total_debt", sum(f.value for f in debt), debt)
    else:
        ctx.gap("financial_snapshot", company.ticker, "total_debt", "debt_not_reported", str(end))
    ocf = operating_cash_flow(gaap, end)
    if ocf:
        note = f"{_fact_note([ocf])}；年初至今 {months(ocf)} 个月累计（{ocf.start} 至 {ocf.end}）"
        record("operating_cash_flow_ytd", ocf.value, [ocf], note)
        snap.operating_cash_flow_months = months(ocf)
    else:
        ctx.gap("financial_snapshot", company.ticker, "operating_cash_flow_ytd", "no_ocf_tag", "")
    shares = shares_outstanding(dei, gaap)
    if shares and (end - shares.end).days > STALE_SHARES_DAYS:
        ctx.gap(
            "financial_snapshot",
            company.ticker,
            "shares_outstanding",
            "shares_stale",
            f"最新流通股日期 {shares.end}，早于资产负债表日 {end} 超过 {STALE_SHARES_DAYS} 天",
        )
        shares = None
    if shares:
        label = "封面页日期" if shares.tag == SHARES else "资产负债表日"
        ns = "dei" if shares.tag == SHARES else "us-gaap"
        record(
            "shares_outstanding",
            shares.value,
            [shares],
            f"{ns}:{shares.tag}；{label} {shares.end}；{shares.form} 申报于 {shares.filed}",
        )

    year = full_year_operating_cash_flow(gaap, end)
    basis = burn_basis(ocf, year)
    if cash and basis:
        burn = -basis.value / months(basis)
        runway = round(snap.cash_and_investments / burn, 1)
        snap.runway_months = runway
        period = "年初至今" if basis is ocf else "最近一个完整财年"
        formula = (
            f"{RUNWAY_NOTE}：{snap.cash_and_investments:,.0f} ÷ "
            f"({-basis.value:,.0f} ÷ {months(basis)}) = {runway}；消耗按{period}"
            f"（{basis.start} 至 {basis.end}），取年初至今与最近完整财年中月均消耗较高者"
        )
        for source_id in dict.fromkeys(
            _filing_source(ctx, f, company.cik, path) for f in (*cash, basis)
        ):
            ctx.claim(
                "financial_snapshot",
                snap.id,
                "runway_months",
                runway,
                source_id,
                kind=ClaimKind.inference,
                confidence=Confidence.medium,
                produced_by=ProducedBy.api,
                note=formula,
            )
    elif ocf:
        ctx.gap(
            "financial_snapshot",
            company.ticker,
            "runway_months",
            "operating_cash_flow_positive",
            f"经营现金流 {ocf.value:,.0f} ≥ 0（最近完整财年亦无现金消耗），不计算资金可支撑时间",
        )

    price = _price(ctx, company)
    if price:
        close, day, price_source = price
        snap.share_price = close
        ctx.claim(
            "financial_snapshot",
            snap.id,
            "share_price",
            close,
            price_source,
            produced_by=ProducedBy.api,
            as_of=day,
            note=f"非官方来源：Nasdaq 网站历史行情；{day} 收盘价（快照日 {SNAPSHOT_DATE}）",
        )
        if shares:
            cap = round(close * shares.value)
            snap.market_cap = cap
            note = (
                f"市值 = {day} 收盘价 {close} × 流通股 {shares.value:,.0f}"
                f"（流通股日期 {shares.end}）"
            )
            ctx.claim(
                "financial_snapshot",
                snap.id,
                "market_cap",
                cap,
                price_source,
                produced_by=ProducedBy.api,
                as_of=day,
                note=note,
            )
            ctx.claim(
                "financial_snapshot",
                snap.id,
                "market_cap",
                cap,
                _filing_source(ctx, shares, company.cik, path),
                produced_by=ProducedBy.api,
                as_of=shares.end,
                note=note,
            )


def ingest(ctx: BuildContext) -> None:
    targets = {t.ticker: t for t in ctx.session.exec(select(Target)).all()}
    for company in candidate_pool(ctx.inputs):
        _snapshot_for(ctx, company, targets[company.ticker])
