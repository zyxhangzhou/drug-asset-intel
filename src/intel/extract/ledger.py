"""Prices, billing windows, the per-call cost ledger and the budget cap."""

import json
import math
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


class BudgetExceeded(RuntimeError):
    """The next call could push spending past the provider's cap."""


class PeakRefused(RuntimeError):
    """The provider is in its peak window and peak runs are not allowed."""


class NoPrice(RuntimeError):
    """The provider has no price table, so its cost cannot be bounded."""


@dataclass(frozen=True)
class Prices:
    input_hit: float
    input_miss: float
    output: float


@dataclass(frozen=True)
class Provider:
    name: str
    match_base_url: str
    offpeak: Prices | None
    peak: Prices | None = None
    peak_windows: tuple[tuple[time, time], ...] = ()
    refuse_peak: bool = False
    budget_cny: float = 0.0
    tz: ZoneInfo = ZoneInfo("Asia/Shanghai")
    request_extra: dict = field(default_factory=dict)  # provider-specific body fields

    def is_peak(self, at: datetime) -> bool:
        local = at.astimezone(self.tz)
        if not self.peak_windows or local.weekday() >= 5:
            return False
        return any(a <= local.time() < b for a, b in self.peak_windows)

    def prices(self, at: datetime) -> Prices:
        if self.offpeak is None:
            raise NoPrice(f"{self.name}: no price table in config/llm.toml; refusing to call")
        return self.peak if self.peak and self.is_peak(at) else self.offpeak

    def tier(self, at: datetime) -> str:
        return "peak" if self.peak and self.is_peak(at) else "offpeak"

    def next_offpeak(self, at: datetime) -> datetime:
        local = at.astimezone(self.tz).replace(second=0, microsecond=0)
        while self.is_peak(local):
            local += timedelta(minutes=1)
        return local


@dataclass(frozen=True)
class LlmConfig:
    max_tokens: int
    chars_per_token: float
    providers: tuple[Provider, ...]

    @classmethod
    def load(cls, path: Path = Path("config/llm.toml")) -> "LlmConfig":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        tz = ZoneInfo(data.get("timezone", "Asia/Shanghai"))
        providers = []
        for name, p in data.get("providers", {}).items():
            windows = []
            for w in p.get("peak_windows", []):
                a, b = w.split("-")
                windows.append((time.fromisoformat(a), time.fromisoformat(b)))
            providers.append(
                Provider(
                    name=name,
                    match_base_url=p["match_base_url"],
                    offpeak=Prices(**p["offpeak"]) if "offpeak" in p else None,
                    peak=Prices(**p["peak"]) if "peak" in p else None,
                    peak_windows=tuple(windows),
                    refuse_peak=p.get("refuse_peak", False),
                    budget_cny=float(p.get("budget_cny", 0.0)),
                    tz=tz,
                    request_extra=p.get("request_extra", {}),
                )
            )
        return cls(data.get("max_tokens", 4000), data.get("chars_per_token", 2.5), tuple(providers))

    def provider_for(self, base_url: str) -> Provider:
        for p in self.providers:
            if p.match_base_url in base_url:
                return p
        raise NoPrice(f"no provider in config/llm.toml matches {base_url}")


def token_split(usage: dict) -> tuple[int, int, int]:
    """(cache-hit input, cache-miss input, output) tokens from a provider's raw usage."""
    prompt = int(usage.get("prompt_tokens") or 0)
    if "prompt_cache_hit_tokens" in usage or "prompt_cache_miss_tokens" in usage:  # DeepSeek
        hit = int(usage.get("prompt_cache_hit_tokens") or 0)
        miss = int(usage.get("prompt_cache_miss_tokens") or 0)
    else:  # OpenAI-style, e.g. Qwen: cached tokens inside prompt_tokens_details
        hit = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
        miss = prompt - hit
    return hit, miss, int(usage.get("completion_tokens") or 0)


def cost_cny(usage: dict, prices: Prices) -> float:
    hit, miss, out = token_split(usage)
    return (hit * prices.input_hit + miss * prices.input_miss + out * prices.output) / 1e6


def estimate_cny(prompt_chars: int, cfg: LlmConfig, prices: Prices) -> float:
    """Worst case: every input token a cache miss, output at the cap."""
    tokens_in = math.ceil(prompt_chars / cfg.chars_per_token)
    return (tokens_in * prices.input_miss + cfg.max_tokens * prices.output) / 1e6


@dataclass
class Ledger:
    path: Path
    _entries: list[dict] | None = field(default=None, repr=False)

    def entries(self) -> list[dict]:
        if self._entries is None:
            self._entries = []
            if self.path.exists():
                for line in self.path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        self._entries.append(json.loads(line))
        return self._entries

    def spent(self, provider: str) -> float:
        return sum(e.get("cost_cny") or 0.0 for e in self.entries() if e["provider"] == provider)

    def check(self, provider: Provider, estimate: float, at: datetime, allow_peak: bool) -> None:
        if provider.refuse_peak and provider.is_peak(at) and not allow_peak:
            nxt = provider.next_offpeak(at)
            raise PeakRefused(
                f"{provider.name} is in its peak window; next off-peak starts "
                f"{nxt:%Y-%m-%d %H:%M} ({provider.tz.key}); pass --allow-peak to run anyway"
            )
        spent = self.spent(provider.name)
        if spent + estimate > provider.budget_cny:
            raise BudgetExceeded(
                f"{provider.name}: spent {spent:.4f} CNY + next call up to {estimate:.4f} CNY "
                f"exceeds the cap {provider.budget_cny:.2f} CNY; no call sent"
            )

    def append(self, entry: dict) -> None:
        self.entries()  # load before writing so the new line is not counted twice
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.entries().append(entry)
