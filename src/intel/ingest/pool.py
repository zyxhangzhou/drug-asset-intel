"""Candidate pool and company name aliases, computed from local inputs only.

Fetchers and build steps share this so that what was fetched and what is matched agree.
"""

import csv
import json
import re
from dataclasses import dataclass

import openpyxl

from intel.ingest import Inputs

SUFFIXES = {
    "inc",
    "incorporated",
    "corp",
    "corporation",
    "co",
    "company",
    "plc",
    "nv",
    "ag",
    "sa",
    "ltd",
    "limited",
    "llc",
    "lp",
    "gmbh",
    "bv",
    "pty",
    "sarl",
    "holding",
    "holdings",
    "group",
}


def normalize_name(name: str) -> str:
    """Lowercase, drop share-class tails, punctuation and corporate suffixes."""
    name = re.split(r"\s+-\s+|\bcommon (stock|shares)\b", name, flags=re.I)[0]
    name = name.lower().replace(".", "").replace("&", " and ")
    words = re.sub(r"[^a-z0-9 ]+", " ", name).split()
    while words and words[-1] in SUFFIXES:
        words.pop()
    return " ".join(words)


def display_name(name: str) -> str:
    """Search-friendly form: the original casing without share-class tails or suffixes."""
    name = re.split(r"\s+-\s+|\bcommon (stock|shares)\b", name, flags=re.I)[0]
    words = name.replace(",", " ").split()
    while words and words[-1].lower().replace(".", "") in SUFFIXES:
        words.pop()
    return " ".join(words)


@dataclass(frozen=True)
class Company:
    ticker: str
    name: str
    cik: str | None
    aliases: tuple[str, ...]  # display forms, used as search terms

    @property
    def alias_keys(self) -> set[str]:
        return {normalize_name(a) for a in self.aliases}


def _verified_exclusions(inputs: Inputs) -> set[str]:
    path = inputs.stage0_exclusions
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["ticker"].strip() for r in csv.DictReader(fh) if (r["verified_by"] or "").strip()}


def _sec_entries(inputs: Inputs) -> dict[str, dict]:
    if not inputs.sec_tickers.exists():
        return {}
    data = json.loads(inputs.sec_tickers.read_text())
    return {e["ticker"].upper().replace(".", "-"): e for e in data.values()}


def _manual_aliases(inputs: Inputs) -> dict[str, list[str]]:
    path = inputs.manual_dir / "sponsor_aliases.csv"
    out: dict[str, list[str]] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                out.setdefault(row["ticker"].strip(), []).append(row["alias"].strip())
    return out


def candidate_pool(inputs: Inputs) -> list[Company]:
    """Index companies not excluded by a verified Stage 0 row."""
    ws = openpyxl.load_workbook(inputs.index_workbook, data_only=True).worksheets[0]
    excluded = _verified_exclusions(inputs)
    sec = _sec_entries(inputs)
    manual = _manual_aliases(inputs)
    pool = []
    for ticker, name, *_ in ws.iter_rows(min_row=2, values_only=True):
        if not ticker or ticker in excluded:
            continue
        ticker, name = str(ticker).strip(), str(name).strip()
        entry = sec.get(ticker.upper().replace(".", "-"))
        aliases = [display_name(name)]
        if entry:
            aliases.append(display_name(entry["title"]))
        aliases += manual.get(ticker, [])
        unique = list(dict.fromkeys(a for a in aliases if a))
        deduped = {normalize_name(a): a for a in reversed(unique)}
        pool.append(
            Company(
                ticker=ticker,
                name=name,
                cik=f"{int(entry['cik_str']):010d}" if entry else None,
                aliases=tuple(a for a in unique if deduped[normalize_name(a)] == a),
            )
        )
    return pool
