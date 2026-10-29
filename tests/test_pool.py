import json
from pathlib import Path

import httpx
import pytest

from intel.fetch import BatchResult, Throttled, meta_path, run_batch, write_cache
from intel.ingest import Inputs
from intel.ingest.pool import Company, candidate_pool, display_name, normalize_name

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Vera Therapeutics, Inc. - Class A Common Stock", "vera therapeutics"),
        ("AbbVie Inc. Common Stock", "abbvie"),
        ("uniQure N.V.", "uniqure"),
        ("CRISPR Therapeutics AG", "crispr therapeutics"),
        ("Scholar Rock Holding Corporation", "scholar rock"),
        ("Viking Therapeutics, Inc.", "viking therapeutics"),
        ("Johnson & Johnson", "johnson and johnson"),
    ],
)
def test_normalize_name_drops_suffixes(raw, expected):
    assert normalize_name(raw) == expected


def test_display_name_keeps_casing():
    assert display_name("Vera Therapeutics, Inc. - Class A Common Stock") == "Vera Therapeutics"


def test_pool_excludes_verified_rows_and_merges_aliases(tmp_path):
    manual = tmp_path / "manual"
    manual.mkdir()
    (manual / "stage0_exclusions.csv").write_text(
        "ticker,category,reason,kind,confidence,source_id,source_type,source_url,"
        "source_title,published_date,accessed_on,verified_by\n"
        "APGE,acquired,x,fact,,S,other,,,,2026-10-29,ZY\n"
        "TWST,non_therapeutic,x,inference,high,S2,other,,,,2026-10-29,\n"
    )
    (manual / "sponsor_aliases.csv").write_text("ticker,alias,note\nVKTX,Viking Tx,test\n")
    raw = tmp_path / "raw"
    (raw / "sec").mkdir(parents=True)
    (raw / "sec" / "company_tickers.json").write_text(
        json.dumps(
            {"0": {"cik_str": 1607678, "ticker": "VKTX", "title": "Viking Therapeutics, Inc."}}
        )
    )
    inputs = Inputs(assignment_dir=ROOT / "docs" / "assignment", raw_dir=raw, manual_dir=manual)
    pool = {c.ticker: c for c in candidate_pool(inputs)}
    assert "APGE" not in pool and "TWST" in pool and len(pool) == 148
    vktx = pool["VKTX"]
    assert vktx.cik == "0001607678"
    assert vktx.aliases == ("Viking Therapeutics", "Viking Tx")


# --- batch plumbing -------------------------------------------------------------------


def company(ticker):
    return Company(ticker=ticker, name=ticker, cik=None, aliases=(ticker,))


def test_one_failing_company_does_not_stop_the_batch(tmp_path):
    def handler(request):
        return httpx.Response(500 if "BAD" in str(request.url) else 200, json={})

    http = Throttled(httpx.Client(transport=httpx.MockTransport(handler)), delay=0)

    def one(c):
        http.get(f"https://x.example/{c.ticker}").raise_for_status()
        (tmp_path / c.ticker).write_text("ok")

    result = run_batch(
        [company("AAA"), company("BAD"), company("CCC")], lambda c: tmp_path / c.ticker, one, False
    )
    assert result.fetched == ["AAA", "CCC"] and "BAD" in result.failed
    log = json.loads(result.write_log(tmp_path / "log").read_text())
    assert "BAD" in log["failed"]


def test_cached_company_is_skipped_unless_refresh(tmp_path):
    (tmp_path / "AAA").write_text("cached")
    calls = []
    result = run_batch([company("AAA")], lambda c: tmp_path / c.ticker, calls.append, False)
    assert result.skipped == ["AAA"] and calls == []
    run_batch([company("AAA")], lambda c: tmp_path / c.ticker, calls.append, True)
    assert len(calls) == 1


def test_rate_limited_request_is_retried():
    responses = iter([httpx.Response(429, headers={"retry-after": "2"}), httpx.Response(200)])
    slept = []
    http = Throttled(
        httpx.Client(transport=httpx.MockTransport(lambda r: next(responses))),
        delay=0,
        sleep=slept.append,
    )
    assert http.get("https://x.example/").status_code == 200
    assert 2.0 in slept


def test_cache_sidecar_records_hash(tmp_path):
    resp = httpx.Response(200, content=b"full", request=httpx.Request("GET", "https://x.example/"))
    from intel.fetch import request_record

    write_cache(tmp_path / "a.json", {"trimmed": True}, [request_record(resp)])
    meta = json.loads(meta_path(tmp_path / "a.json").read_text())
    assert meta["requests"][0]["url"] == "https://x.example/"
    assert len(meta["requests"][0]["sha256"]) == 64 and meta["fetched_at"]


def test_batch_result_defaults():
    assert BatchResult().failed == {}
