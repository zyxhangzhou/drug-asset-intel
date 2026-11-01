"""Build step: load accepted items of signed extraction review files, rechecked against archives."""

import calendar
import re
from datetime import date, datetime
from pathlib import Path

from sqlmodel import select

from intel.db import archived_source, sha256_file
from intel.docs.documents import Document, read_documents
from intel.docs.text import normalize
from intel.enums import CatalystType, ClaimKind, Confidence, ProducedBy
from intel.extract import review
from intel.extract.run import asset_key, asset_names
from intel.extract.trials import TrialMatcher, matcher_for
from intel.extract.validate import quote_problem
from intel.ingest import BuildContext
from intel.models import Catalyst, Program, Source, Target, TrialResult

NOTE = "LLM 抽取，经人工复核接受；原文片段在构建时重新校验"


class ExtractionLoadError(ValueError):
    """An accepted item no longer checks out against its archived document."""


# --- timing -> window -----------------------------------------------------------------

ORDINAL = {"first": 1, "second": 2, "third": 3, "fourth": 4, "1st": 1, "2nd": 2, "3rd": 3, "4th": 4}


def _span(year: int, m1: int, m2: int) -> tuple[date, date]:
    return date(year, m1, 1), date(year, m2, calendar.monthrange(year, m2)[1])


def parse_window(timing: str) -> tuple[date, date] | None:
    """Window for a quarter, half, mid-year, year-end or bare year; None for anything else."""
    t = normalize(timing).removesuffix(".")
    if len(set(re.findall(r"20\d\d", t))) != 1:
        return None
    year = int(re.search(r"20\d\d", t).group())
    q = re.search(r"\b(?:q([1-4])|([1-4])q)\b", t)
    word = re.search(r"\b(first|second|third|fourth|1st|2nd|3rd|4th) quarter\b", t)
    if q or word:
        n = int(q.group(1) or q.group(2)) if q else ORDINAL[word.group(1)]
        return _span(year, 3 * n - 2, 3 * n)
    h = re.search(r"\b(?:h([12])|([12])h)\b", t)
    word = re.search(r"\b(first|second|1st|2nd) half\b", t)
    if h or word:
        n = int(h.group(1) or h.group(2)) if h else ORDINAL[word.group(1)]
        return _span(year, 1, 6) if n == 1 else _span(year, 7, 12)
    if re.search(r"\bmid-? ?20\d\d\b", t):
        return _span(year, 6, 8)
    if re.search(r"\b(end of|year-end|year end|by the end of)\b", t):
        return _span(year, 10, 12)
    if re.fullmatch(r"(in |during |by )?(calendar |fiscal )?(year )?20\d\d", t):
        return _span(year, 1, 12)
    return None


# --- matching -------------------------------------------------------------------------


def _key(s: str) -> str:
    return re.sub(r"[^0-9a-z]", "", normalize(s))


MIN_CONTAINED_CHARS = 5


def match_program(programs: list[Program], asset: str) -> Program | None:
    """By name, name without brackets or bracketed code; else a unique containment."""
    names = asset_names(asset)
    if not names:
        return None
    hits = [p for p in programs if asset_names(p.name) & names]
    if len(hits) > 1:  # "RGX-121" also names "RGX-121 (...)": prefer the same full name
        hits = [p for p in hits if asset_key(p.name) == asset_key(asset)] or hits
        if len({asset_key(p.name) for p in hits}) > 1:
            return None
    if hits:
        return hits[0]
    key = _key(asset)
    partial = [p for p in programs if key in _key(p.name)]
    if partial:
        return partial[0] if len(partial) == 1 else None
    # "ABBV-RGX-314 (sura-vec)" contains the program name "RGX-314" as whole words;
    # "ARO-DUX4" does not contain "ARO-DUX".
    words = _words(asset)
    inside = [p for p in programs if len(_key(p.name)) >= MIN_CONTAINED_CHARS
              and _contains_words(words, _words(p.name))]  # fmt: skip
    return inside[0] if len(inside) == 1 else None


def _words(s: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[0-9a-z]+", normalize(s)))


def _contains_words(hay: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    n = len(needle)
    return n > 0 and any(hay[i : i + n] == needle for i in range(len(hay) - n + 1))


# --- sources --------------------------------------------------------------------------


def document_source(
    ctx: BuildContext, docs: dict[str, Document], source_id: str, where: str
) -> Source:
    """The archived source of an item; registers DOC- sources and fills archive fields."""
    doc = docs.get(source_id)
    if doc is None:
        raise ExtractionLoadError(f"{where}: {source_id} is not in {ctx.inputs.documents}")
    docs_dir = ctx.inputs.docs_dir
    meta = doc.meta(docs_dir)
    path = doc.text_path(docs_dir)
    if not meta or meta.get("status") != "ok" or not path.exists():
        raise ExtractionLoadError(f"{where}: {source_id} has no archived text at {path}")
    if sha256_file(path) != meta["text_sha256"]:
        raise ExtractionLoadError(
            f"{where}: {source_id} archive changed since fetch (hash differs)"
        )
    source = ctx.session.get(Source, source_id)
    if source is None:
        published = _full_date(doc.published_date)
        source = archived_source(
            source_id,
            doc.source_type,
            path,
            url=doc.url,
            title=doc.title,
            published_date=published,
            fetched_at=datetime.fromisoformat(meta["fetched_at"]),
        )
        source.published_date_text = doc.published_date
        source.note = doc.note
        ctx.session.add(source)
    else:
        source.local_path = str(path)
        source.content_hash = meta["text_sha256"]
    ctx.session.flush()
    return source


def _full_date(text: str | None) -> date | None:
    try:
        return date.fromisoformat(text) if text else None
    except ValueError:
        return None


# --- step -----------------------------------------------------------------------------


def ingest(ctx: BuildContext) -> None:
    signed = review.load_signed(ctx.inputs.extractions_dir)
    if not signed:
        return
    docs = {d.source_id: d for d in read_documents(ctx.inputs.documents)[0]}
    texts: dict[str, str] = {}
    trials = matcher_for(ctx, docs)
    undecided = loaded = 0
    for path, rev in signed:
        target = ctx.session.exec(select(Target).where(Target.ticker == rev.ticker)).first()
        if target is None:
            raise ExtractionLoadError(f"{path.name}: unknown ticker {rev.ticker}")
        for item in rev.items:
            if item.decision != "accept":
                undecided += item.decision == ""
                continue
            where = f"{path.name} item {item.id}"
            source = document_source(ctx, docs, item.source_id, where)
            if item.source_id not in texts:
                texts[item.source_id] = normalize(Path(source.local_path).read_text("utf-8"))
            problem = quote_problem(item.quotes, item.values, texts[item.source_id])
            if problem:
                raise ExtractionLoadError(f"{where}: {problem}")
            problem = _value_problem(item)
            if problem:
                raise ExtractionLoadError(f"{where}: {problem}")
            loaded += _write(ctx, path, target, item, source, trials)
    ctx.notes.append(f"extractions: {loaded} accepted item(s) loaded, {undecided} not reviewed")


PLACEHOLDERS = {"", "none", "n/a", "na", "not reported", "not stated"}


def _value_problem(item) -> str | None:
    """Controlled values a reviewer may have edited by hand."""
    v = item.values
    if item.type == "catalyst" and v.get("event_type") not in {t.value for t in CatalystType}:
        return f"event_type {v.get('event_type')!r} is not one of {[t.value for t in CatalystType]}"
    if item.type == "clinical_result" and v.get("advantage_vs_soc"):
        if v.get("confidence") not in {c.value for c in Confidence}:
            return "advantage_vs_soc needs confidence high, medium_high, medium or low"
    return None


def _write(
    ctx: BuildContext, path: Path, target: Target, item, source: Source, trials: TrialMatcher
) -> int:
    v = item.values
    claim = dict(
        produced_by=ProducedBy.llm,
        model=item.returned_model or item.model,
        quote=" … ".join(item.quotes),
        as_of=source.published_date,
        note=NOTE,
    )
    location = f"{path.name}#{item.id}"
    programs = list(target.programs)
    if item.type == "program":
        program = match_program(programs, v["asset"])
        if program is None:
            ctx.gap("program", target.ticker, v["asset"], "extraction_unmatched", location)
            return 0
        for fld in ("mechanism", "modality"):
            if not v.get(fld):
                continue
            current = getattr(program, fld)
            if current and current != v[fld]:
                ctx.gap("program", program.name, fld, "extraction_conflict", location)
                continue
            setattr(program, fld, v[fld])
            ctx.claim("program", program.id, fld, v[fld], source.source_id, **claim)
        return 1
    if item.type == "clinical_result":
        found = trials.match(target, v.get("trial", ""))
        if found.trial is None:
            ctx.gap(
                "trial_result", target.ticker, v.get("trial") or "trial", found.reason, location
            )
            return 0
        trial = found.trial
        if found.basis:
            claim["note"] = f"{NOTE}；{found.basis}"
        fields = ("endpoint", "result", "analysis", "comparator", "advantage_vs_soc")
        # "none" means the model found nothing to quote; a quote cannot show a comparator is absent.
        given = {f: v.get(f) if (v.get(f) or "").strip().lower() not in PLACEHOLDERS else None
                 for f in fields}  # fmt: skip
        row = TrialResult(trial_id=trial.id, **{f: given[f] or None for f in fields})
        ctx.session.add(row)
        ctx.session.flush()
        for fld in fields:
            if not given[fld]:
                continue
            if fld == "advantage_vs_soc":
                ctx.claim("trial_result", row.id, fld, v[fld], source.source_id,
                          kind=ClaimKind.inference, confidence=Confidence(v["confidence"]),
                          **claim)  # fmt: skip
            else:
                ctx.claim("trial_result", row.id, fld, v[fld], source.source_id, **claim)
        return 1
    program = match_program(programs, v.get("asset", ""))
    window = parse_window(v["timing"])
    event = f"{v['event']}（{v['timing']}）"
    row = Catalyst(
        target_id=target.id,
        program_id=program.id if program else None,
        event=event,
        event_type=CatalystType(v["event_type"]),
        window_start=window[0] if window else None,
        window_end=window[1] if window else None,
    )
    ctx.session.add(row)
    ctx.session.flush()
    ctx.claim("catalyst", row.id, "event", event, source.source_id, **claim)
    if window:
        for fld, day in (("window_start", window[0]), ("window_end", window[1])):
            ctx.claim("catalyst", row.id, fld, day.isoformat(), source.source_id, **claim)
    else:
        ctx.gap("catalyst", target.ticker, "window", "timing_not_parsed", location)
    return 1
