import dataclasses
import json
from pathlib import Path

import httpx
import pytest

from intel import fetch
from intel.config import load_settings
from intel.enums import LinkStatus
from intel.ingest import Inputs

ROOT = Path(__file__).resolve().parents[1]


def client_for(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def never_called(request):
    raise AssertionError(f"unexpected request to {request.url}")


def settings(**overrides):
    return dataclasses.replace(load_settings(), **overrides)


def test_sec_fetch_without_contact_fails_without_request(tmp_path):
    inputs = Inputs(raw_dir=tmp_path)
    with pytest.raises(fetch.MissingConfig, match="SEC_USER_AGENT"):
        fetch.fetch_sec_tickers(settings(sec_user_agent=None), inputs, client_for(never_called))
    assert not inputs.sec_tickers.exists()


def test_sec_fetch_saves_raw_response(tmp_path):
    seen = {}

    def handler(request):
        seen["ua"] = request.headers["user-agent"]
        return httpx.Response(200, json={"0": {"cik_str": 1, "ticker": "X", "title": "X"}})

    inputs = Inputs(raw_dir=tmp_path)
    path = fetch.fetch_sec_tickers(
        settings(sec_user_agent="Test test@x.org"), inputs, client_for(handler)
    )
    assert seen["ua"] == "Test test@x.org"
    assert json.loads(path.read_text())["0"]["ticker"] == "X"
    assert fetch.read_fetched_at(path) is not None


@pytest.mark.parametrize(
    ("code", "expected"),
    [(200, LinkStatus.ok), (403, LinkStatus.blocked), (404, LinkStatus.broken)],
)
def test_classify_by_status(code, expected):
    status, http = fetch.classify_link(
        "https://a.example/x", client_for(lambda r: httpx.Response(code))
    )
    assert (status, http) == (expected, code)


def test_head_not_allowed_falls_back_to_get():
    def handler(request):
        return httpx.Response(405 if request.method == "HEAD" else 200)

    assert fetch.classify_link("https://a.example/x", client_for(handler))[0] == LinkStatus.ok


def test_dns_failure_is_broken():
    def handler(request):
        raise httpx.ConnectError("name resolution failed")

    assert fetch.classify_link("https://nope.invalid/", client_for(handler))[0] == LinkStatus.broken


def test_local_path_is_not_fetched():
    status, _ = fetch.classify_link(r"D:\横店资本\patent_cliff", client_for(never_called))
    assert status == LinkStatus.local_file


def test_fetch_links_records_every_register_row(tmp_path):
    inputs = Inputs(assignment_dir=ROOT / "docs" / "assignment", raw_dir=tmp_path)
    path = fetch.fetch_links(
        inputs, client_for(lambda r: httpx.Response(200)), sleep=lambda _: None
    )
    results = json.loads(path.read_text())
    assert len(results) == 43
    statuses = [r["status"] for r in results.values()]
    assert statuses.count("local_file") == 1 and statuses.count("ok") == 42
