"""The hand-kept document list (`data/manual/documents.csv`) and where each document is archived."""

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from intel.enums import SourceType

COLUMNS = ("ticker", "url", "source_type", "title", "published_date", "source_id", "note")
DOCUMENT_TYPES = {
    SourceType.sec_filing,
    SourceType.press_release,
    SourceType.company_ir,
    SourceType.publication,
    SourceType.fda_web,
}


@dataclass(frozen=True)
class Document:
    line: int
    ticker: str
    url: str
    source_type: SourceType
    title: str | None
    published_date: str | None  # as written: YYYY-MM-DD or YYYY-MM
    source_id: str
    note: str | None

    def folder(self, docs_dir: Path) -> Path:
        return docs_dir / self.ticker

    def text_path(self, docs_dir: Path) -> Path:
        return self.folder(docs_dir) / f"{self.source_id}.txt"

    def meta_path(self, docs_dir: Path) -> Path:
        return self.folder(docs_dir) / f"{self.source_id}.meta.json"

    def meta(self, docs_dir: Path) -> dict | None:
        path = self.meta_path(docs_dir)
        return json.loads(path.read_text()) if path.exists() else None

    def text(self, docs_dir: Path) -> str | None:
        meta = self.meta(docs_dir)
        if not meta or meta.get("status") != "ok":
            return None
        return self.text_path(docs_dir).read_text(encoding="utf-8")


def generated_id(ticker: str, url: str) -> str:
    return f"DOC-{ticker}-{hashlib.sha256(url.encode()).hexdigest()[:8]}"


def read_documents(path: Path) -> tuple[list[Document], list[tuple[int, str]]]:
    """Valid rows, and (line number, reason) for every rejected row."""
    if not path.exists():
        return [], []
    docs, errors, seen = [], [], set()
    with path.open(encoding="utf-8", newline="") as fh:
        for line, row in enumerate(csv.DictReader(fh), start=2):
            row = {k: (v or "").strip() for k, v in row.items() if k}
            ticker, url = row.get("ticker", "").upper(), row.get("url", "")
            if not ticker:
                errors.append((line, "ticker is empty"))
                continue
            if not url.lower().startswith(("http://", "https://")):
                errors.append((line, f"url is not http(s): {url!r}"))
                continue
            try:
                kind = SourceType(row.get("source_type", ""))
            except ValueError:
                kind = None
            if kind not in DOCUMENT_TYPES:
                errors.append((line, f"source_type {row.get('source_type')!r} not allowed"))
                continue
            source_id = row.get("source_id") or generated_id(ticker, url)
            if source_id in seen:
                errors.append((line, f"duplicate source_id {source_id}"))
                continue
            seen.add(source_id)
            docs.append(
                Document(
                    line=line,
                    ticker=ticker,
                    url=url,
                    source_type=kind,
                    title=row.get("title") or None,
                    published_date=row.get("published_date") or None,
                    source_id=source_id,
                    note=row.get("note") or None,
                )
            )
    return docs, errors
