"""Quote and number checks shared by extraction and the snapshot build."""

import re
from dataclasses import dataclass

from intel.docs.text import normalize, numbers
from intel.enums import CatalystType
from intel.extract.tasks import CONFIDENCE_VALUES, NUMBER_CHECKED, Task

MIN_QUOTE_CHARS = 20


@dataclass(frozen=True)
class Item:
    type: str
    values: dict[str, str]
    quotes: tuple[str, ...]
    spans: tuple[tuple[int, int], ...]  # positions of the quotes in the normalised text


def quote_problem(quotes: list[str], values: dict[str, str], doc_norm: str) -> str | None:
    """Why the quotes do not support the values, or None when they do."""
    if not quotes:
        return "no_quote"
    for q in quotes:
        nq = normalize(q)
        if len(nq) < MIN_QUOTE_CHARS:
            return "quote_too_short"
        if nq not in doc_norm:
            return "quote_not_in_text"
    # Digits of the asset code (VK2735) are a name, not a reported number.
    in_quotes = set().union(*(numbers(q) for q in quotes), numbers(values.get("asset", "")))
    for name in NUMBER_CHECKED:
        missing = numbers(values.get(name, "")) - in_quotes
        if missing:
            return f"number_not_in_quote:{name}={','.join(sorted(missing))}"
    return None


def spans(quotes: list[str], doc_norm: str) -> tuple[tuple[int, int], ...]:
    out = []
    for q in quotes:
        nq = normalize(q)
        start = doc_norm.find(nq)
        out.append((start, start + len(nq)))
    return tuple(out)


def check_item(task: Task, raw: object, doc_norm: str) -> tuple[Item | None, str | None]:
    """A model item turned into a checked Item, or the reason it is rejected."""
    if not isinstance(raw, dict):
        return None, "not_an_object"
    values = {f: str(raw.get(f) or "").strip() for f in task.fields}
    for f in task.required:
        if not values[f]:
            return None, f"missing_field:{f}"
    if task.name == "program" and not (values["mechanism"] or values["modality"]):
        return None, "no_value"
    if task.name == "catalyst" and values["event_type"] not in {t.value for t in CatalystType}:
        return None, "bad_event_type"
    if task.name == "catalyst" and not re.search(r"\b20\d\d\b", values["timing"]):
        return None, "timing_without_year"
    if task.name == "clinical_result":
        confidence = str(raw.get("confidence") or "").strip()
        if values["advantage_vs_soc"]:
            if confidence not in CONFIDENCE_VALUES:
                return None, "advantage_without_confidence"
            values["confidence"] = confidence
    quotes = raw.get("quotes") or []
    if isinstance(quotes, str):
        quotes = [quotes]
    quotes = [str(q).strip() for q in quotes if str(q).strip()]
    problem = quote_problem(quotes, values, doc_norm)
    if problem:
        return None, problem
    return Item(task.name, values, tuple(quotes), spans(quotes, doc_norm)), None
