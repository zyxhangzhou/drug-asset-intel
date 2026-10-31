"""`intel extract`: retrieve chunks, extract with the primary model, check, cross-check blind."""

import hashlib
import json
import os
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from intel.docs.documents import Document
from intel.docs.index import ChunkIndex
from intel.docs.text import normalize, numbers
from intel.extract import review
from intel.extract.client import CallResult, LlmClient
from intel.extract.tasks import NUMBER_CHECKED, SYSTEM_PROMPT, TASKS, Task, user_prompt
from intel.extract.validate import Item, check_item

CHUNKS_PER_TASK = 4


@dataclass
class RunSummary:
    calls: int = 0
    cost_cny: float = 0.0
    estimate_cny: float = 0.0
    items: Counter = field(default_factory=Counter)  # agreed / disputed / single
    rejected: Counter = field(default_factory=Counter)  # reason -> count
    added: int = 0
    skipped_docs: list[str] = field(default_factory=list)


# "avutometinib plus defactinib" and "AVUTOMETINIB DEFACTINIB" name the same regimen.
CONNECTORS = {"plus", "and", "with", "combination", "combined"}


def _asset_key(asset: str) -> str:
    return "".join(w for w in re.findall(r"[0-9a-z]+", normalize(asset)) if w not in CONNECTORS)


def pair_key(item: Item) -> tuple:
    v = item.values
    if item.type == "program":
        return (_asset_key(v["asset"]),)
    if item.type == "clinical_result":
        trial = re.sub(r"[^0-9a-z]", "", normalize(v.get("trial", "")))
        return (_asset_key(v["asset"]), trial or normalize(v["endpoint"]), normalize(v["endpoint"]))
    years = tuple(sorted(re.findall(r"20\d\d", v["timing"])))
    return (_asset_key(v.get("asset", "")), v["event_type"], years)


def _asset_names(asset: str) -> set[str]:
    """The whole name, the name without its brackets, and each bracketed code."""
    n = normalize(asset)
    parts = [n, re.sub(r"\([^)]*\)", " ", n), *re.findall(r"\(([^)]*)\)", n)]
    return {k for k in map(_asset_key, parts) if k}


def same_asset(a: Item, b: Item) -> bool:
    """'BARZOLVOLIMAB' and 'BARZOLVOLIMAB (CDX-0159)' are one drug."""
    x, y = _asset_names(a.values.get("asset", "")), _asset_names(b.values.get("asset", ""))
    return bool(x & y) or not (x or y)


def same_key(a: Item, b: Item) -> bool:
    return same_asset(a, b) and pair_key(a)[1:] == pair_key(b)[1:]


def overlap(a: Item, b: Item) -> bool:
    return any(s1 < e2 and s2 < e1 for s1, e1 in a.spans for s2, e2 in b.spans)


def same_passage(a: Item, b: Item) -> bool:
    """Fallback pairing when the keys differ only in wording: same asset, overlapping quotes."""
    return same_asset(a, b) and overlap(a, b)


# Ways of saying a field is empty; the prompt offers "none" for a trial without a comparator.
NO_VALUE = {"none", "n/a", "na", "not stated", "not reported", "-"}


def _value(item: Item, name: str) -> str:
    v = item.values.get(name, "")
    return "" if normalize(v) in NO_VALUE else v


def agree(a: Item, b: Item) -> bool:
    """Field by field: both empty, or same numbers and (same text or overlapping quotes)."""
    quotes_overlap = overlap(a, b)
    for name in NUMBER_CHECKED:
        x, y = _value(a, name), _value(b, name)
        if not x and not y:
            continue
        if not x or not y or numbers(x) != numbers(y):
            return False
        if normalize(x) != normalize(y) and not quotes_overlap:
            return False
    return True


ID_PREFIX = {"program": "p", "clinical_result": "r", "catalyst": "e"}


def item_id(source_id: str, kind: str, key: tuple, taken: set[str]) -> str:
    """Stable across reruns of the same document, so reviewer decisions survive a rerun."""
    digest = hashlib.sha256(f"{source_id}|{kind}|{json.dumps(key)}".encode()).hexdigest()[:8]
    base = f"{ID_PREFIX[kind]}-{digest}"
    uid, n = base, 2
    while uid in taken:
        uid, n = f"{base}-{n}", n + 1
    taken.add(uid)
    return uid


@dataclass
class Extractor:
    primary: LlmClient
    verify: LlmClient | None
    index: ChunkIndex
    docs_dir: Path
    log_path: Path  # validation outcome of every model item
    programs: Callable[[str], list[str]] = lambda ticker: []
    dry_run: bool = False
    summary: RunSummary = field(default_factory=RunSummary)

    def run_document(self, doc: Document, tasks: list[str]) -> list[review.ReviewItem]:
        text = doc.text(self.docs_dir)
        if not text:
            self.summary.skipped_docs.append(f"{doc.source_id}: not archived or no text")
            return []
        meta = doc.meta(self.docs_dir)
        chunks = self.index.add(doc.source_id, text, meta["text_sha256"])
        doc_norm = normalize(text)
        out: list[review.ReviewItem] = []
        taken: set[str] = set()
        for name in tasks:
            task = TASKS[name]
            sent = (
                chunks
                if len(chunks) == 1
                else self.index.search(doc.source_id, task.query, CHUNKS_PER_TASK)
            )
            if not sent:
                continue
            prompt = user_prompt(task, doc.ticker, self.programs(doc.ticker), sent)
            meta_call = {"task": name, "ticker": doc.ticker, "source_id": doc.source_id,
                         "chunks": [c.no for c in sent]}  # fmt: skip
            if self.dry_run:
                self.summary.estimate_cny += self.primary.estimate(SYSTEM_PROMPT, prompt)
                if self.verify:
                    self.summary.estimate_cny += self.verify.estimate(SYSTEM_PROMPT, prompt)
                continue
            mine = self._extract(self.primary, task, prompt, meta_call, doc_norm)
            theirs = None
            if self.verify:
                theirs = self._extract(self.verify, task, prompt, meta_call, doc_norm)
            out += self._pair(doc, task, mine, theirs, taken)
        return out

    def _extract(self, client: LlmClient, task: Task, prompt: str, meta: dict, doc_norm: str):
        result = client.complete(SYSTEM_PROMPT, prompt, meta=meta)
        self.summary.calls += 1
        self.summary.cost_cny += result.cost_cny
        raw_items = (result.content or {}).get("items", [])
        if not isinstance(raw_items, list):
            raw_items = []
        items = []
        # A replay re-pairs saved replies; their checks are already in the log.
        log = os.devnull if result.replayed else self.log_path
        with open(log, "a", encoding="utf-8") as fh:
            for raw in raw_items:
                item, reason = check_item(task, raw, doc_norm)
                fh.write(
                    json.dumps(
                        {
                            "call_id": result.call_id,
                            "provider": client.provider.name,
                            "role": client.endpoint.role,
                            **meta,
                            "ok": item is not None,
                            "reason": reason,
                            "item": raw,
                        },  # fmt: skip
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                if item:
                    items.append(item)
                else:
                    self.summary.rejected[reason.split(":")[0]] += 1
        return result, items

    def _pair(
        self,
        doc: Document,
        task: Task,
        mine: tuple[CallResult, list[Item]],
        theirs: tuple[CallResult, list[Item]] | None,
        taken: set[str],
    ) -> list[review.ReviewItem]:
        result, items = mine
        pool = list(theirs[1]) if theirs else []
        out = []
        for item in items:
            match = next((o for o in pool if same_key(o, item)), None) or next(
                (o for o in pool if same_passage(o, item)), None
            )
            if match:
                pool.remove(match)
            check = (
                "single"
                if theirs is None
                else "agreed"
                if match and agree(item, match)
                else "disputed"
            )
            out.append(self._review_item(doc, item, result, check, match, taken))
        for other in pool:  # only the cross-check model found these
            out.append(self._review_item(doc, other, theirs[0], "disputed", None, taken,
                                         model=self.verify.endpoint.model))  # fmt: skip
        for r in out:
            self.summary.items[r.check] += 1
        return out

    def _review_item(self, doc, item, result, check, match, taken, model=None):
        return review.ReviewItem(
            id=item_id(doc.source_id, item.type, pair_key(item), taken),
            type=item.type,
            source_id=doc.source_id,
            values=dict(item.values),
            quotes=list(item.quotes),
            model=model or self.primary.endpoint.model,
            returned_model=result.returned_model or "",
            check=check,
            verify=dict(match.values) if match else None,
            verify_quotes=list(match.quotes) if match else [],
            decision="accept" if check == "agreed" else "",
        )
