"""Match a trial named in a document (SHASTA-3, VANQUISH 1) to a trial in the snapshot."""

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from sqlmodel import select

from intel.docs.text import normalize
from intel.models import Source, Target, Trial

TOKEN_RE = re.compile(r"[a-z]+|\d+")
NCT_RE = re.compile(r"NCT\d{8}")
MAX_PREFIX_CHARS = 40
ALIAS_COLUMNS = ("ticker", "name", "nct_id", "source_id", "note", "verified_by")
GENERIC = {
    "phase", "part", "study", "trial", "cohort", "stage", "arm", "period", "extension", "open",
    "label", "dose", "escalation", "expansion", "long", "term", "followup", "follow", "up", "and",
    "or", "a", "an", "the", "of", "in", "with", "for", "lte", "ole", "mg", "week", "weeks",
}  # fmt: skip
NAME_LIKE = re.compile(r"\d|\b[A-Z]{5,}\b")


class TrialAliasError(ValueError):
    """The manual trial alias file is malformed."""


def tokens(text: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(normalize(text)))


def _contains(hay: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    n = len(needle)
    return any(hay[i : i + n] == needle for i in range(len(hay) - n + 1))


def registry_names(study: dict, acronyms: frozenset[str] = frozenset()) -> list[str]:
    """Names a CT.gov record gives a trial: acronym, parenthesised names, the title's prefix.

    Parenthesised names and title prefixes count only when they look like a study name
    (VANQUISH 2, AFFINITY DUCHENNE, or "Venture Oral Dosing" where VENTURE is another trial's
    acronym), not a disease abbreviation such as (DMD).
    """
    ident = study["protocolSection"]["identificationModule"]
    names = [ident["acronym"]] if ident.get("acronym") else []
    title = ident.get("briefTitle") or ""
    candidates = re.findall(r"\(([^()]+)\)", title)
    prefix = title.split(":", 1)[0] if ":" in title else ""
    if prefix and len(prefix) <= MAX_PREFIX_CHARS:
        candidates.append(prefix)
    for c in candidates:
        words = tokens(c)
        if NAME_LIKE.search(c) or (words and words[0] in acronyms):
            names.append(c)
    return names


@dataclass(frozen=True)
class Alias:
    tokens: tuple[str, ...]
    nct_id: str
    basis: str  # how the name is known to mean this trial, written into the claim note


@dataclass(frozen=True)
class Match:
    trial: Trial | None
    basis: str | None
    reason: str | None  # gap reason when trial is None


def _usable(name_tokens: tuple[str, ...]) -> bool:
    joined = "".join(name_tokens)
    specific = [t for t in name_tokens if t.isalpha() and t not in GENERIC]
    return len(joined) >= 4 and bool(specific)


def manual_aliases(path: Path, known_source) -> dict[str, list[Alias]]:
    """Signed rows of the manual alias file, by ticker. Unsigned rows are ignored."""
    out: dict[str, list[Alias]] = {}
    if not path.exists():
        return out
    with path.open(encoding="utf-8", newline="") as fh:
        for line, row in enumerate(csv.DictReader(fh), start=2):
            row = {k: (v or "").strip() for k, v in row.items() if k}
            if not row.get("verified_by"):
                continue
            nct, source_id = row.get("nct_id", "").upper(), row.get("source_id", "")
            if not NCT_RE.fullmatch(nct) or not row.get("name"):
                raise TrialAliasError(f"{path.name}:{line}: needs a name and an NCT number")
            if not known_source(source_id):
                raise TrialAliasError(f"{path.name}:{line}: source {source_id!r} is not registered")
            basis = (
                f"试验按人工对照表对照：「{row['name']}」→ {nct}（来源 {source_id}，"
                f"复核 {row['verified_by']}）"
            )
            out.setdefault(row["ticker"].upper(), []).append(Alias(tokens(row["name"]), nct, basis))
    return out


class TrialMatcher:
    def __init__(self, session, ctgov_dir: Path, manual: dict[str, list[Alias]]):
        self.session = session
        self.ctgov_dir = ctgov_dir
        self.manual = manual
        self._registry: dict[str, list[Alias]] = {}

    def _trials(self, target: Target) -> dict[str, Trial]:
        rows = self.session.exec(select(Trial).where(Trial.target_id == target.id)).all()
        return {t.nct_id: t for t in rows}

    def registry_aliases(self, target: Target) -> list[Alias]:
        if target.ticker in self._registry:
            return self._registry[target.ticker]
        trials = self._trials(target)
        program_keys = {tokens(p.name) for p in target.programs}
        found: dict[tuple[str, ...], set[tuple[str, str]]] = {}
        path = self.ctgov_dir / f"{target.ticker}.json"
        studies = json.loads(path.read_text())["studies"] if path.exists() else []
        studies = [
            st for st in studies if st["protocolSection"]["identificationModule"]["nctId"] in trials
        ]
        acronyms = frozenset(
            tokens(ident["acronym"])[0]
            for ident in (st["protocolSection"]["identificationModule"] for st in studies)
            if ident.get("acronym") and tokens(ident["acronym"])
        )
        for study in studies:
            nct = study["protocolSection"]["identificationModule"]["nctId"]
            for name in registry_names(study, acronyms):
                key = tokens(name)
                if _usable(key) and key not in program_keys:
                    found.setdefault(key, set()).add((nct, name))
        aliases = []
        for key, hits in found.items():
            ncts = {n for n, _ in hits}
            if len(ncts) == 1:  # a name shared by several trials identifies none of them
                nct, name = sorted(hits)[0]
                aliases.append(Alias(key, nct, f"试验按 CT.gov 登记名称对照：「{name}」→ {nct}"))
        self._registry[target.ticker] = aliases
        return aliases

    def match(self, target: Target, text: str) -> Match:
        trials = self._trials(target)
        nct = NCT_RE.search((text or "").upper())
        if nct:
            trial = trials.get(nct.group())
            return Match(trial, None, None if trial else "extraction_unmatched")
        hay = tokens(text or "")
        hits = [
            a
            for a in [*self.registry_aliases(target), *self.manual.get(target.ticker, [])]
            if a.nct_id in trials and _contains(hay, a.tokens)
        ]
        # The most specific name wins: "MUIR-3" over "MUIR", "RAMP 201J" over "RAMP 201".
        hits = [
            a
            for a in hits
            if not any(b.tokens != a.tokens and _contains(b.tokens, a.tokens) for b in hits)
        ]
        ncts = {a.nct_id for a in hits}
        if not ncts:
            return Match(None, None, "extraction_unmatched")
        if len(ncts) > 1:
            return Match(None, None, "extraction_trial_ambiguous")
        return Match(trials[hits[0].nct_id], hits[0].basis, None)


def matcher_for(ctx, docs: dict) -> TrialMatcher:
    def known(source_id: str) -> bool:
        return source_id in docs or ctx.session.get(Source, source_id) is not None

    manual = manual_aliases(ctx.inputs.trial_aliases, known)
    return TrialMatcher(ctx.session, ctx.inputs.raw_dir / "ctgov", manual)
