"""Network fetches. Each writes the raw response under data/raw/ and never touches the snapshot."""

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import httpx

from intel.config import Settings
from intel.enums import LinkStatus
from intel.ingest import Inputs

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
BLOCKED_CODES = {401, 403, 429}
BROKEN_CODES = {404, 410}


class MissingConfig(RuntimeError):
    """A fetch needs a setting that is not configured."""


def _write_raw(path: Path, content: bytes, url: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    meta = {"url": url, "fetched_at": datetime.now(UTC).isoformat()}
    path.with_name(path.stem + ".meta.json").write_text(json.dumps(meta, indent=2))


def read_fetched_at(path: Path) -> datetime | None:
    meta = path.with_name(path.stem + ".meta.json")
    if not meta.exists():
        return None
    return datetime.fromisoformat(json.loads(meta.read_text())["fetched_at"])


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
    _write_raw(inputs.sec_tickers, resp.content, SEC_TICKERS_URL)
    return inputs.sec_tickers


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
            sleep(0.5)
    path = inputs.link_results
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    return path


def http_client() -> httpx.Client:
    return httpx.Client(timeout=15, follow_redirects=True)
