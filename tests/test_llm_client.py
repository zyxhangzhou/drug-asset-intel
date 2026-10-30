import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from intel.extract.client import Endpoint, LlmClient, LlmError
from intel.extract.ledger import (
    BudgetExceeded,
    Ledger,
    LlmConfig,
    NoPrice,
    PeakRefused,
    Prices,
    cost_cny,
    estimate_cny,
)

ROOT = Path(__file__).resolve().parents[1]
CFG = LlmConfig.load(ROOT / "config" / "llm.toml")
DEEPSEEK = CFG.provider_for("https://api.deepseek.com")
# 2026-11-04 is a Wednesday; 02:00 UTC is 10:00 in Beijing.
WED_10 = datetime(2026, 11, 4, 2, 0, tzinfo=UTC)
WED_20 = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
SAT_10 = datetime(2026, 11, 7, 2, 0, tzinfo=UTC)


def test_peak_windows_follow_beijing_weekdays():
    assert DEEPSEEK.is_peak(WED_10)
    assert not DEEPSEEK.is_peak(WED_20)
    assert not DEEPSEEK.is_peak(SAT_10)
    assert not DEEPSEEK.is_peak(datetime(2026, 11, 4, 4, 30, tzinfo=UTC))  # 12:30 lunch break
    assert DEEPSEEK.next_offpeak(WED_10).strftime("%H:%M") == "12:00"


def test_cache_hit_and_miss_priced_separately():
    usage = {"prompt_cache_hit_tokens": 1_000_000, "prompt_cache_miss_tokens": 1_000_000,
             "completion_tokens": 1_000_000, "prompt_tokens": 2_000_000}  # fmt: skip
    assert cost_cny(usage, DEEPSEEK.prices(WED_20)) == pytest.approx(0.15 + 4.5 + 13.5)
    assert cost_cny(usage, DEEPSEEK.prices(WED_10)) == pytest.approx(0.30 + 9.0 + 27.0)


def test_openai_style_cached_tokens():
    usage = {"prompt_tokens": 1000, "completion_tokens": 0,
             "prompt_tokens_details": {"cached_tokens": 400}}  # fmt: skip
    assert cost_cny(usage, Prices(1, 10, 0)) == pytest.approx((400 + 6000) / 1e6)


def test_estimate_is_worst_case():
    est = estimate_cny(2500, CFG, Prices(0, 4.5, 13.5))
    assert est == pytest.approx((1000 * 4.5 + CFG.max_tokens * 13.5) / 1e6)


def test_budget_cap_refuses_before_call(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.append({"provider": "deepseek", "cost_cny": 14.9})
    with pytest.raises(BudgetExceeded, match="14.9"):
        ledger.check(DEEPSEEK, 0.2, WED_20, allow_peak=False)
    ledger.check(DEEPSEEK, 0.05, WED_20, allow_peak=False)


def test_peak_refused_unless_allowed(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    with pytest.raises(PeakRefused, match="12:00"):
        ledger.check(DEEPSEEK, 0.01, WED_10, allow_peak=False)
    ledger.check(DEEPSEEK, 0.01, WED_10, allow_peak=True)


def test_missing_price_table_refused(tmp_path):
    path = tmp_path / "llm.toml"
    path.write_text('[providers.x]\nmatch_base_url = "x.example"\nbudget_cny = 5\n')
    cfg = LlmConfig.load(path)
    with pytest.raises(NoPrice):
        cfg.provider_for("https://x.example/v1").prices(WED_20)
    with pytest.raises(NoPrice):
        cfg.provider_for("https://unknown.example")


# --- client ---------------------------------------------------------------------------


def reply(content: str, finish: str = "stop") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "deepseek-v4-pro-1017",
            "choices": [{"message": {"content": content}, "finish_reason": finish}],
            "usage": {
                "prompt_tokens": 1000,
                "prompt_cache_hit_tokens": 0,
                "prompt_cache_miss_tokens": 1000,
                "completion_tokens": 200,
            },  # fmt: skip
        },
    )


def client_with(tmp_path, responses: list[httpx.Response], now=WED_20):
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return responses.pop(0)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    ep = Endpoint("primary", "https://api.deepseek.com", "deepseek-v4-pro", "k")
    client = LlmClient(ep, CFG, Ledger(tmp_path / "ledger.jsonl"), http, tmp_path / "resp",
                       now=lambda: now, sleep=lambda s: None)  # fmt: skip
    return client, sent


def test_call_records_usage_cost_and_raw_response(tmp_path):
    client, sent = client_with(tmp_path, [reply('{"items": []}')])
    result = client.complete("sys", "user", meta={"task": "program", "source_id": "S"})
    assert result.content == {"items": []}
    assert result.returned_model == "deepseek-v4-pro-1017"
    assert sent[0]["temperature"] == 0 and sent[0]["response_format"] == {"type": "json_object"}
    entry = client.ledger.entries()[0]
    assert entry["usage"]["prompt_cache_miss_tokens"] == 1000
    assert entry["cost_cny"] == pytest.approx((1000 * 4.5 + 200 * 13.5) / 1e6)
    assert entry["tier"] == "offpeak" and entry["task"] == "program"
    assert (tmp_path / "resp" / f"{result.call_id}.json").exists()


def test_server_errors_retried(tmp_path):
    client, sent = client_with(tmp_path, [httpx.Response(503), httpx.Response(500),
                                          reply('{"items": []}')])  # fmt: skip
    assert client.complete("s", "u", meta={}).content == {"items": []}
    assert len(sent) == 3


def test_gives_up_after_retries(tmp_path):
    client, _ = client_with(tmp_path, [httpx.Response(503)] * 3)
    with pytest.raises(LlmError, match="3 attempts"):
        client.complete("s", "u", meta={})
    assert client.ledger.entries() == []


def test_bad_json_is_recorded_not_retried(tmp_path):
    client, sent = client_with(tmp_path, [reply("not json"), reply('{"a":', "length")])
    assert client.complete("s", "u", meta={}).content is None
    assert client.complete("s", "u", meta={}).content is None
    assert len(sent) == 2
    statuses = [e["status"] for e in client.ledger.entries()]
    assert statuses[0].startswith("bad_json") and "truncated" in statuses[1]


def test_budget_refusal_sends_nothing(tmp_path):
    client, sent = client_with(tmp_path, [reply("{}")])
    client.ledger.append({"provider": "deepseek", "cost_cny": 15.0})
    with pytest.raises(BudgetExceeded):
        client.complete("s", "u", meta={})
    assert sent == []


def test_peak_refusal_sends_nothing(tmp_path):
    client, sent = client_with(tmp_path, [reply("{}")], now=WED_10)
    with pytest.raises(PeakRefused):
        client.complete("s", "u", meta={})
    assert sent == []


def test_thinking_disabled_per_provider(tmp_path):
    client, sent = client_with(tmp_path, [reply('{"items": []}')])
    client.complete("s", "u", meta={})
    assert sent[0]["thinking"] == {"type": "disabled"}
    qwen = CFG.provider_for("https://ws-x.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
    assert qwen.request_extra == {"enable_thinking": False}
