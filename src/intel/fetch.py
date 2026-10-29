"""Network fetches. Each writes raw responses under data/raw/ and never touches the snapshot.

Caches may be trimmed to the fields the build uses; the sidecar `<name>.meta.json` keeps the
request URLs and the sha256 of every full response so a trimmed cache can be re-verified.
"""

import hashlib
import json
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx

from intel.config import Settings
from intel.enums import LinkStatus
from intel.ingest import Inputs
from intel.ingest.pool import Company

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
BLOCKED_CODES = {401, 403, 429}
BROKEN_CODES = {404, 410}

SEC_DELAY = 0.12  # SEC fair access: at most 10 requests per second
DEFAULT_DELAY = 0.5
CTGOV_DELAY = 1.3  # ClinicalTrials.gov allows roughly 50 requests per minute


class MissingConfig(RuntimeError):
    """A fetch needs a setting that is not configured."""


# --- cache files ----------------------------------------------------------------------


def meta_path(path: Path) -> Path:
    return path.with_name(path.stem + ".meta.json")


def request_record(resp: httpx.Response) -> dict[str, str]:
    return {"url": str(resp.request.url), "sha256": hashlib.sha256(resp.content).hexdigest()}


def write_cache(path: Path, data: object, requests: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True))
    meta = {"fetched_at": datetime.now(UTC).isoformat(), "requests": requests}
    meta_path(path).write_text(json.dumps(meta, indent=2))


def _write_raw(path: Path, resp: httpx.Response) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    meta = {"fetched_at": datetime.now(UTC).isoformat(), "requests": [request_record(resp)]}
    meta_path(path).write_text(json.dumps(meta, indent=2))


def read_fetched_at(path: Path) -> datetime | None:
    meta = meta_path(path)
    if not meta.exists():
        return None
    return datetime.fromisoformat(json.loads(meta.read_text())["fetched_at"])


def first_request_url(path: Path) -> str | None:
    meta = meta_path(path)
    if not meta.exists():
        return None
    reqs = json.loads(meta.read_text()).get("requests") or []
    return reqs[0]["url"] if reqs else None


# --- batch plumbing -------------------------------------------------------------------


@dataclass
class Throttled:
    """A client wrapper that spaces requests out."""

    client: httpx.Client
    delay: float = DEFAULT_DELAY
    sleep: Callable[[float], None] = time.sleep
    headers: dict[str, str] = field(default_factory=dict)
    _last: float = 0.0

    retries: int = 3

    def get(self, url: str, **kwargs) -> httpx.Response:
        headers = self.headers | kwargs.pop("headers", {})
        for attempt in range(self.retries + 1):
            wait = self._last + self.delay - time.monotonic()
            if wait > 0:
                self.sleep(wait)
            self._last = time.monotonic()
            resp = self.client.get(url, headers=headers, **kwargs)
            if resp.status_code != 429 or attempt == self.retries:
                return resp
            retry_after = resp.headers.get("retry-after", "")
            self.sleep(float(retry_after) if retry_after.isdigit() else 15.0 * (attempt + 1))
        return resp


@dataclass
class BatchResult:
    fetched: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)

    def write_log(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "_fetch_log.json"
        log = {
            "finished_at": datetime.now(UTC).isoformat(),
            "fetched": self.fetched,
            "skipped_cached": self.skipped,
            "failed": self.failed,
        }
        path.write_text(json.dumps(log, indent=2, ensure_ascii=False))
        return path


def run_batch(
    companies: Iterable[Company],
    cache_for: Callable[[Company], Path],
    fetch_one: Callable[[Company], None],
    refresh: bool,
) -> BatchResult:
    """Fetch per company; a failure is logged and the batch continues."""
    result = BatchResult()
    for company in companies:
        if cache_for(company).exists() and not refresh:
            result.skipped.append(company.ticker)
            continue
        try:
            fetch_one(company)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            result.failed[company.ticker] = f"{type(exc).__name__}: {exc}"
        else:
            result.fetched.append(company.ticker)
    return result


# --- SEC ------------------------------------------------------------------------------


def sec_headers(settings: Settings) -> dict[str, str]:
    if not settings.sec_user_agent:
        raise MissingConfig(
            "SEC_USER_AGENT is not set; SEC requires a contact, "
            'add a line like SEC_USER_AGENT="Your Name you@example.com" to .env'
        )
    return {"User-Agent": settings.sec_user_agent}


def fetch_sec_tickers(settings: Settings, inputs: Inputs, client: httpx.Client) -> Path:
    resp = client.get(SEC_TICKERS_URL, headers=sec_headers(settings))
    resp.raise_for_status()
    _write_raw(inputs.sec_tickers, resp)
    return inputs.sec_tickers


# --- links ----------------------------------------------------------------------------


def classify_link(url: str | None, client: httpx.Client) -> tuple[LinkStatus, int | None]:
    if not url or not url.lower().startswith(("http://", "https://")):
        return LinkStatus.local_file, None
    try:
        resp = client.head(url)
        if resp.status_code in (405, 501) or resp.status_code >= 500:
            resp = client.get(url)
    except httpx.ConnectError:
        return LinkStatus.broken, None
    except httpx.HTTPError:
        return LinkStatus.unchecked, None
    code = resp.status_code
    if code < 400:
        return LinkStatus.ok, code
    if code in BLOCKED_CODES:
        return LinkStatus.blocked, code
    if code in BROKEN_CODES:
        return LinkStatus.broken, code
    return LinkStatus.unchecked, code


def fetch_links(
    inputs: Inputs,
    client: httpx.Client,
    sleep: Callable[[float], None] = time.sleep,
) -> Path:
    from intel.ingest.mnc import read_source_register

    results = {}
    for row in read_source_register(inputs.mnc_workbook):
        status, code = classify_link(row.url, client)
        results[row.source_id] = {
            "url": row.url,
            "status": status.value,
            "http_status": code,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        if status is not LinkStatus.local_file:
            sleep(DEFAULT_DELAY)
    path = inputs.link_results
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    return path


def http_client() -> httpx.Client:
    return httpx.Client(timeout=60, follow_redirects=True)
