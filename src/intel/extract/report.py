"""`intel extract report`: cost, check pass rates and model agreement from the run records."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from intel.extract import review
from intel.extract.ledger import Ledger, token_split

QUOTE_REASONS = ("no_quote", "quote_too_short", "quote_not_in_text")


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _rate(ok: int, total: int) -> str:
    return f"{ok}/{total} ({ok / total:.0%})" if total else "0/0"


def report(llm_dir: Path, extractions_dir: Path) -> list[str]:
    lines = ["== cost by provider =="]
    usage: dict[str, Counter] = defaultdict(Counter)
    for e in Ledger(llm_dir / "ledger.jsonl").entries():
        hit, miss, out = token_split(e.get("usage") or {})
        u = usage[e["provider"]]
        u.update(calls=1, input_hit=hit, input_miss=miss, output=out)
        u["bad_json"] += str(e.get("status", "")).startswith("bad_json")
        u["cost_milli_fen"] += round((e.get("cost_cny") or 0) * 100_000)
    for name, u in sorted(usage.items()):
        lines.append(
            f"{name}: {u['calls']} calls ({u['bad_json']} bad JSON), input "
            f"{u['input_hit'] + u['input_miss']} tokens ({u['input_hit']} cache hit), output "
            f"{u['output']} tokens, cost {u['cost_milli_fen'] / 100_000:.4f} CNY"
        )

    lines.append("== checks by company and model ==")
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for v in _jsonl(llm_dir / "validation.jsonl"):
        groups[(v.get("ticker", ""), v.get("provider", ""))].append(v)
    reasons: Counter = Counter()
    for (ticker, provider), rows in sorted(groups.items()):
        kinds = [(r["reason"] or "").split(":")[0] for r in rows]
        # Field checks run before the quote check; those items never reached it.
        reached = [k for k in kinds if k in ("", "number_not_in_quote", *QUOTE_REASONS)]
        quoted = [k for k in reached if k not in QUOTE_REASONS]
        lines.append(
            f"{ticker} {provider}: {len(rows)} items, {sum(r['ok'] for r in rows)} kept; quote "
            f"check {_rate(len(quoted), len(reached))}; number check "
            f"{_rate(quoted.count(''), len(quoted))}"
        )
        reasons.update((r["reason"] or "").split(":")[0] for r in rows if not r["ok"])
    listed = ", ".join(f"{k} {n}" for k, n in reasons.most_common())
    lines.append(f"rejection reasons: {listed or 'none'}")

    lines.append("== cross-check agreement (review files) ==")
    if extractions_dir.exists():
        for path in sorted(extractions_dir.glob("*.toml")):
            r = review.parse(path)
            checks = Counter(i.check for i in r.items)
            decisions = Counter(i.decision or "undecided" for i in r.items)
            paired = checks["agreed"] + checks["disputed"]
            lines.append(
                f"{r.ticker}: agreed {_rate(checks['agreed'], paired)}, single "
                f"{checks['single']}; decisions {dict(decisions)}; signed: "
                f"{r.verified_by or 'no'}"
            )
    return lines
