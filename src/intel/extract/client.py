"""OpenAI-compatible chat client with a budget check before and a ledger entry after every call."""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx

from intel.config import Settings
from intel.extract.ledger import Ledger, LlmConfig, Provider, cost_cny, estimate_cny

RETRIES = 2
TIMEOUT = 180


class LlmError(RuntimeError):
    """The provider rejected the request or kept failing."""


@dataclass(frozen=True)
class Endpoint:
    role: str  # primary | verify
    base_url: str
    model: str
    api_key: str


def endpoints(settings: Settings) -> tuple[Endpoint | None, Endpoint | None]:
    def make(role, url, model, key):
        return Endpoint(role, url.rstrip("/"), model, key) if url and model and key else None

    return (
        make("primary", settings.llm_base_url, settings.llm_model, settings.llm_api_key),
        make(
            "verify",
            settings.llm_verify_base_url,
            settings.llm_verify_model,
            settings.llm_verify_api_key,
        ),
    )


@dataclass(frozen=True)
class CallResult:
    call_id: str
    content: dict | None  # parsed JSON object, None when the reply was not valid JSON
    returned_model: str | None
    cost_cny: float


@dataclass
class LlmClient:
    endpoint: Endpoint
    cfg: LlmConfig
    ledger: Ledger
    http: httpx.Client
    responses_dir: Path
    allow_peak: bool = False
    now: Callable[[], datetime] = field(default=lambda: datetime.now(UTC))
    sleep: Callable[[float], None] = time.sleep

    @property
    def provider(self) -> Provider:
        return self.cfg.provider_for(self.endpoint.base_url)

    def estimate(self, system: str, user: str) -> float:
        return estimate_cny(len(system) + len(user), self.cfg, self.provider.prices(self.now()))

    def complete(self, system: str, user: str, *, meta: dict) -> CallResult:
        provider = self.provider
        at = self.now()
        prices = provider.prices(at)
        self.ledger.check(provider, self.estimate(system, user), at, self.allow_peak)
        body = {
            "model": self.endpoint.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": self.cfg.max_tokens,
            "response_format": {"type": "json_object"},
            **provider.request_extra,
        }
        data = self._post(body)
        call_id = f"{at:%Y%m%dT%H%M%S%f}-{provider.name}"
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        (self.responses_dir / f"{call_id}.json").write_text(
            json.dumps({"request_meta": meta, "response": data}, indent=1, ensure_ascii=False)
        )
        usage = data.get("usage") or {}
        cost = cost_cny(usage, prices)
        content, status = None, "ok"
        choice = (data.get("choices") or [{}])[0]
        try:
            if choice.get("finish_reason") == "length":
                raise ValueError("output truncated at max_tokens")
            content = json.loads(choice["message"]["content"])
            if not isinstance(content, dict):
                raise ValueError("reply is not a JSON object")
        except (KeyError, TypeError, ValueError) as exc:
            content, status = None, f"bad_json: {exc}"
        self.ledger.append(
            {
                "call_id": call_id,
                "ts": at.isoformat(),
                "provider": provider.name,
                "role": self.endpoint.role,
                "requested_model": self.endpoint.model,
                "returned_model": data.get("model"),
                **meta,
                "usage": usage,
                "tier": provider.tier(at),
                "cost_cny": round(cost, 6),
                "status": status,
            }
        )
        return CallResult(call_id, content, data.get("model"), cost)

    def _post(self, body: dict) -> dict:
        url = f"{self.endpoint.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.endpoint.api_key}"}
        last = ""
        for attempt in range(RETRIES + 1):
            try:
                resp = self.http.post(url, json=body, headers=headers, timeout=TIMEOUT)
            except httpx.TimeoutException as exc:
                last = f"timeout: {exc}"
            else:
                if resp.status_code < 400:
                    return resp.json()
                if resp.status_code < 500 and resp.status_code != 429:
                    raise LlmError(
                        f"{self.endpoint.role}: HTTP {resp.status_code}: {resp.text[:300]}"
                    )
                last = f"HTTP {resp.status_code}"
            if attempt < RETRIES:
                self.sleep(5.0 * (attempt + 1))
        raise LlmError(f"{self.endpoint.role}: gave up after {RETRIES + 1} attempts ({last})")
