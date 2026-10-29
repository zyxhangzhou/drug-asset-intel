import json
from datetime import date
from pathlib import Path

import httpx
import pytest
from sqlmodel import Session, select

from intel.build import build_snapshot
from intel.config import load_settings
from intel.db import rw_engine
from intel.enums import ClaimKind
from intel.fetch import Throttled, meta_path, write_cache
from intel.ingest import Inputs
from intel.ingest import financials as fin
from intel.ingest.pool import Company
from intel.models import Claim, FinancialSnapshot, Source, Target

ROOT = Path(__file__).resolve().parents[1]
END = "2026-06-30"


def instant(val, end=END, accn="0000000000-26-000001", form="10-Q", filed="2026-08-05"):
    return {"val": val, "end": end, "accn": accn, "form": form, "filed": filed}


def duration(val, start="2026-01-01", end=END, **kw):
    return instant(val, end=end, **kw) | {"start": start}


def facts(gaap: dict[str, list], shares=None, taxonomies=("dei", "us-gaap")) -> dict:
    return {
        "cik": 1,
        "entityName": "Test Co",
        "taxonomies": list(taxonomies),
        "us-gaap": {tag: {"USD": entries} for tag, entries in gaap.items()},
        "dei": {fin.SHARES: {"shares": shares}} if shares else {},
    }


def gaap_units(data: dict) -> dict:
    return data["us-gaap"]


# --- selection rules ------------------------------------------------------------------


def test_components_summed_when_no_combined_tag():
    g = gaap_units(
        facts(
            {
                fin.CASH: [instant(100.0)],
                "AvailableForSaleSecuritiesDebtSecuritiesCurrent": [instant(400.0)],
            }
        )
    )
    parts = fin.cash_and_investments(g, date.fromisoformat(END))
    assert sum(p.value for p in parts) == 500.0 and len(parts) == 2


def test_combined_tag_is_not_double_counted():
    g = gaap_units(
        facts(
            {
                "CashCashEquivalentsAndShortTermInvestments": [instant(500.0)],
                fin.CASH: [instant(100.0)],
                "ShortTermInvestments": [instant(400.0)],
            }
        )
    )
    (only,) = fin.cash_and_investments(g, date.fromisoformat(END))
    assert only.tag == "CashCashEquivalentsAndShortTermInvestments" and only.value == 500.0


def test_unclassified_total_used_only_without_split():
    g = gaap_units(
        facts(
            {
                fin.CASH: [instant(100.0)],
                "ShortTermInvestments": [instant(300.0)],
                "Investments": [instant(999.0)],
            }
        )
    )
    assert sum(p.value for p in fin.cash_and_investments(g, date.fromisoformat(END))) == 400.0


def test_restated_value_wins_and_late_filings_ignored():
    g = gaap_units(
        facts(
            {
                fin.CASH: [
                    instant(100.0, filed="2026-08-05"),
                    instant(110.0, filed="2026-09-01", accn="0000000000-26-000002"),
                    instant(999.0, end="2026-09-30", filed="2026-11-05"),  # after snapshot date
                ]
            }
        )
    )
    assert fin._anchor(g) == date.fromisoformat(END)
    (cash,) = fin.cash_and_investments(g, date.fromisoformat(END))
    assert cash.value == 110.0


def test_ytd_operating_cash_flow_prefers_longest_period():
    g = gaap_units(
        facts(
            {
                fin.OCF: [
                    duration(-50.0, start="2026-04-01"),
                    duration(-120.0, start="2026-01-01"),
                ]
            }
        )
    )
    ocf = fin.operating_cash_flow(g, date.fromisoformat(END))
    assert ocf.value == -120.0 and fin.months(ocf) == 6


# --- build ----------------------------------------------------------------------------


def write_company(raw: Path, ticker: str, cik: str, data: dict | None, rows: list | None):
    sec = raw / "sec"
    sec.mkdir(parents=True, exist_ok=True)
    tickers = sec / "company_tickers.json"
    entries = json.loads(tickers.read_text()) if tickers.exists() else {}
    entries[str(len(entries))] = {"cik_str": int(cik), "ticker": ticker, "title": ticker}
    tickers.write_text(json.dumps(entries))
    if data:
        write_cache(fin.xbrl_cache(Inputs(raw_dir=raw), cik.zfill(10)), data, [])
    if rows:
        write_cache(fin.price_cache(Inputs(raw_dir=raw), ticker), {"rows": rows}, [])


SHARES = [instant(200_000_000.0, end="2026-07-31")]
PRICE_ROWS = [
    {"date": "10/27/2026", "close": "$9.00"},
    {"date": "10/23/2026", "close": "$8.00"},
]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("fin")
    raw = tmp / "raw"
    burning = facts(
        {
            fin.CASH: [instant(200_000_000.0)],
            "ShortTermInvestments": [instant(300_000_000.0)],
            fin.OCF: [duration(-240_000_000.0)],
        },
        shares=SHARES,
    )
    profitable = facts(
        {fin.CASH: [instant(900_000_000.0)], fin.OCF: [duration(50_000_000.0)]}, shares=SHARES
    )
    write_company(raw, "VKTX", "1607678", burning, PRICE_ROWS)
    write_company(raw, "MDGL", "1157601", profitable, None)
    write_company(raw, "QURE", "1590560", facts({}, taxonomies=("dei", "ifrs-full")), None)
    inputs = Inputs(assignment_dir=ROOT / "docs" / "assignment", raw_dir=raw, manual_dir=tmp / "m")
    db = tmp / "intel.db"
    return db, build_snapshot(db, inputs)


@pytest.fixture
def s(built):
    with Session(rw_engine(built[0])) as session:
        yield session


def snapshot(s, ticker) -> FinancialSnapshot:
    target = s.exec(select(Target).where(Target.ticker == ticker)).one()
    return s.exec(select(FinancialSnapshot).where(FinancialSnapshot.target_id == target.id)).one()


def claims(s, snap, field):
    return s.exec(
        select(Claim).where(
            Claim.entity_type == "financial_snapshot",
            Claim.entity_id == str(snap.id),
            Claim.field == field,
        )
    ).all()


def test_runway_from_burn(s):
    snap = snapshot(s, "VKTX")
    assert snap.cash_and_investments == 500_000_000.0
    assert snap.runway_months == 12.5
    (c,) = claims(s, snap, "runway_months")
    assert c.kind == ClaimKind.inference and "÷" in c.note


def test_filed_values_cite_the_filing(s):
    snap = snapshot(s, "VKTX")
    (c,) = claims(s, snap, "cash_and_investments")
    assert c.kind == ClaimKind.fact and c.source_id == "SEC-0000000000-26-000001"
    assert "ShortTermInvestments" in c.note
    src = s.get(Source, c.source_id)
    assert src.url == "https://www.sec.gov/Archives/edgar/data/1607678/000000000026000001/"


def test_weekend_snapshot_uses_previous_close_and_market_cap_cites_both(s):
    snap = snapshot(s, "VKTX")
    assert snap.share_price == 9.0
    (price,) = claims(s, snap, "share_price")
    assert price.source_id == "NASDAQ-VKTX-2026-10-27" and "非官方" in price.note
    assert snap.market_cap == 1_800_000_000
    sources = {c.source_id for c in claims(s, snap, "market_cap")}
    assert sources == {"NASDAQ-VKTX-2026-10-27", "SEC-0000000000-26-000001"}


def test_positive_cash_flow_has_no_runway(s, built):
    assert snapshot(s, "MDGL").runway_months is None
    assert any(
        g.key == "MDGL" and g.reason == "operating_cash_flow_positive" for g in built[1].gaps
    )


def test_foreign_filer_is_a_gap(s, built):
    target = s.exec(select(Target).where(Target.ticker == "QURE")).one()
    assert target.financials == []
    assert any(g.key == "QURE" and g.reason == "no_us_gaap" for g in built[1].gaps)


def test_snapshot_passes_provenance(s):
    from intel.db import provenance_gaps

    assert provenance_gaps(s) == []


# --- fetch ----------------------------------------------------------------------------


def test_trimmed_cache_keeps_verbatim_entries(tmp_path):
    entry = {
        "end": END,
        "val": 5,
        "accn": "a",
        "fy": 2026,
        "fp": "Q2",
        "form": "10-Q",
        "filed": "2026-08-01",
    }
    full = {
        "cik": 1,
        "entityName": "X",
        "facts": {
            "us-gaap": {
                fin.CASH: {"label": "Cash", "units": {"USD": [entry]}},
                "Revenues": {"units": {"USD": [entry]}},
            },
            "dei": {fin.SHARES: {"units": {"shares": [entry]}}},
        },
    }

    def handler(request):
        assert request.headers["user-agent"] == "Test t@x.org"
        return httpx.Response(200, json=full)

    import dataclasses

    settings = dataclasses.replace(load_settings(), sec_user_agent="Test t@x.org")
    http = Throttled(httpx.Client(transport=httpx.MockTransport(handler)), delay=0)
    company = Company("X", "X", "0000000001", ("X",))
    fin.fetch_xbrl(Inputs(raw_dir=tmp_path), http, [company], settings)
    path = fin.xbrl_cache(Inputs(raw_dir=tmp_path), "0000000001")
    cached = json.loads(path.read_text())
    assert cached["us-gaap"] == {fin.CASH: {"USD": [entry]}}  # Revenues dropped, entry verbatim
    assert len(json.loads(meta_path(path).read_text())["requests"][0]["sha256"]) == 64
