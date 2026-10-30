"""Fetch listed documents into `data/raw/docs/<TICKER>/`; list EDGAR filings to pick from."""

import hashlib
import html
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

from intel.config import Settings
from intel.docs.documents import Document
from intel.docs.text import to_text
from intel.fetch import BLOCKED_CODES, SEC_DELAY, BatchResult, Throttled, sec_headers

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
INDEX_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{accession}-index.html"
EDGAR = "https://www.sec.gov"


def is_sec(url: str) -> bool:
    return bool(re.match(r"https?://([a-z]+\.)?sec\.gov/", url, re.I))


def _extension(content_type: str, url: str) -> str:
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        return ".pdf"
    if "html" in content_type:
        return ".html"
    return ".raw"


def fetch_one(doc: Document, http: Throttled, docs_dir: Path) -> str:
    """Archive one document; returns its status (ok or no_text). Raises on HTTP failure."""
    resp = http.get(doc.url)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    text = to_text(resp.content, content_type, doc.url)
    folder = doc.folder(docs_dir)
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(f"{doc.source_id}.orig.*"):
        old.unlink()
    raw_path = folder / f"{doc.source_id}.orig{_extension(content_type, doc.url)}"
    raw_path.write_bytes(resp.content)
    doc.text_path(docs_dir).write_text(text, encoding="utf-8")
    status = "ok" if text.strip() else "no_text"
    meta = {
        "source_id": doc.source_id,
        "url": doc.url,
        "final_url": str(resp.url),
        "fetched_at": datetime.now(UTC).isoformat(),
        "content_type": content_type,
        "raw_file": raw_path.name,
        "raw_sha256": hashlib.sha256(resp.content).hexdigest(),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "status": status,
    }
    doc.meta_path(docs_dir).write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return status


def fetch_documents(
    docs: Iterable[Document],
    client: httpx.Client,
    settings: Settings,
    docs_dir: Path,
    refresh: bool = False,
) -> BatchResult:
    """Fetch every listed document not yet archived; one failure never stops the batch."""
    docs = list(docs)
    sec = other = None
    result = BatchResult()
    log = []
    for doc in docs:
        if doc.meta(docs_dir) and not refresh:
            result.skipped.append(doc.source_id)
            continue
        if is_sec(doc.url):
            sec = sec or Throttled(client, delay=SEC_DELAY, headers=sec_headers(settings))
            http = sec
        else:
            other = other or Throttled(client)
            http = other
        entry = {"at": datetime.now(UTC).isoformat(), "source_id": doc.source_id, "url": doc.url}
        try:
            status = fetch_one(doc, http, docs_dir)
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            status = "blocked" if code in BLOCKED_CODES else "failed"
            result.failed[doc.source_id] = f"{status}: HTTP {code}"
            entry["http_status"] = code
        except httpx.HTTPError as exc:
            status = "failed"
            result.failed[doc.source_id] = f"failed: {type(exc).__name__}: {exc}"
        else:
            result.fetched.append(doc.source_id)
            if status == "no_text":
                result.failed[doc.source_id] = "no_text: nothing extractable (scanned PDF?)"
        log.append(entry | {"status": status})
    if log:
        docs_dir.mkdir(parents=True, exist_ok=True)
        with (docs_dir / "fetch_log.jsonl").open("a", encoding="utf-8") as fh:
            for entry in log:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return result


# --- EDGAR filing discovery -----------------------------------------------------------


@dataclass(frozen=True)
class Exhibit:
    description: str
    kind: str
    url: str


@dataclass(frozen=True)
class Filing:
    filed: str
    form: str
    accession: str
    primary_url: str
    exhibits: list[Exhibit]


ROW_RE = re.compile(r"(?is)<tr[^>]*>(.*?)</tr>")
CELL_RE = re.compile(r"(?is)<td[^>]*>(.*?)</td>")
HREF_RE = re.compile(r'(?i)href="([^"]+)"')


def parse_index(page: str) -> list[Exhibit]:
    """Documents of a filing index page, without images."""
    exhibits = []
    table = page.split('summary="Document Format Files"', 1)[-1].split("</table>", 1)[0]
    for row in ROW_RE.findall(table):
        cells = CELL_RE.findall(row)
        if len(cells) < 4:
            continue
        href = HREF_RE.search(cells[2])
        kind = html.unescape(re.sub(r"<[^>]+>", "", cells[3])).strip()
        if not href or kind in ("GRAPHIC", "ZIP", "XML") or kind.startswith("EX-101"):
            continue
        path = href.group(1).removeprefix("/ix?doc=")
        description = html.unescape(re.sub(r"<[^>]+>", "", cells[1])).strip()
        exhibits.append(Exhibit(description, kind, EDGAR + path))
    return exhibits


def cik_for(ticker: str, tickers_json: Path) -> int:
    for row in json.loads(tickers_json.read_text()).values():
        if row["ticker"].upper() == ticker.upper():
            return int(row["cik_str"])
    raise KeyError(f"{ticker} not in {tickers_json}")


def list_filings(
    cik: int, forms: set[str], client: httpx.Client, settings: Settings, limit: int = 15
) -> list[Filing]:
    http = Throttled(client, delay=SEC_DELAY, headers=sec_headers(settings))
    resp = http.get(SUBMISSIONS_URL.format(cik=cik))
    resp.raise_for_status()
    recent = resp.json()["filings"]["recent"]
    filings = []
    for i, form in enumerate(recent["form"]):
        if form not in forms:
            continue
        accession = recent["accessionNumber"][i]
        folder = accession.replace("-", "")
        base = f"{EDGAR}/Archives/edgar/data/{cik}/{folder}"
        index = http.get(INDEX_URL.format(cik=cik, folder=folder, accession=accession))
        index.raise_for_status()
        filings.append(
            Filing(
                filed=recent["filingDate"][i],
                form=form,
                accession=accession,
                primary_url=f"{base}/{recent['primaryDocument'][i]}",
                exhibits=parse_index(index.text),
            )
        )
        if len(filings) >= limit:
            break
    return filings
