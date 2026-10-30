"""Per-company extraction review files: `data/manual/extractions/<TICKER>.toml`."""

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from intel.extract.tasks import TASKS

DECISIONS = ("accept", "reject", "")
CHECKS = ("agreed", "disputed", "single")


class ExtractionReviewError(ValueError):
    """An extraction review file is malformed."""


@dataclass
class ReviewItem:
    id: str
    type: str
    source_id: str
    values: dict[str, str]
    quotes: list[str]
    model: str
    returned_model: str
    check: str
    verify: dict[str, str] | None = None
    verify_quotes: list[str] = field(default_factory=list)
    decision: str = ""
    note: str = ""


@dataclass
class ExtractionReview:
    ticker: str
    verified_by: str = ""
    items: list[ReviewItem] = field(default_factory=list)


def _value_fields(kind: str) -> tuple[str, ...]:
    extra = ("confidence",) if kind == "clinical_result" else ()
    return TASKS[kind].fields + extra


def parse(path: Path) -> ExtractionReview:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        review = ExtractionReview(data["ticker"], str(data.get("verified_by", "")).strip())
        for raw in data.get("items", []):
            kind = raw["type"]
            if kind not in TASKS:
                raise ExtractionReviewError(f"unknown item type {kind!r}")
            if raw.get("decision", "") not in DECISIONS:
                raise ExtractionReviewError(f"{raw['id']}: decision must be accept, reject or ''")
            review.items.append(
                ReviewItem(
                    id=raw["id"],
                    type=kind,
                    source_id=raw["source_id"],
                    values={f: str(raw.get(f, "")) for f in _value_fields(kind)},
                    quotes=list(raw.get("quotes", [])),
                    model=raw.get("model", ""),
                    returned_model=raw.get("returned_model", ""),
                    check=raw.get("check", ""),
                    verify=raw.get("verify"),
                    verify_quotes=list(raw.get("verify_quotes", [])),
                    decision=raw.get("decision", ""),
                    note=raw.get("note", ""),
                )
            )
    except (KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        raise ExtractionReviewError(f"{path.name}: {exc!r}") from exc
    except ExtractionReviewError as exc:
        raise ExtractionReviewError(f"{path.name}: {exc}") from exc
    return review


def _s(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def dumps(review: ExtractionReview) -> str:
    lines = [
        "# LLM extraction review. Set decision per item (accept / reject), then sign verified_by.",
        "# Only accepted items of a signed file enter the snapshot; quotes are rechecked at build.",
        f"ticker = {_s(review.ticker)}",
        f"verified_by = {_s(review.verified_by)}",
    ]
    for item in review.items:
        lines += ["", "[[items]]", f"id = {_s(item.id)}", f"type = {_s(item.type)}",
                  f"source_id = {_s(item.source_id)}"]  # fmt: skip
        for name in _value_fields(item.type):
            lines.append(f"{name} = {_s(item.values.get(name, ''))}")
        lines.append(f"quotes = {_s(item.quotes)}")
        lines += [f"model = {_s(item.model)}", f"returned_model = {_s(item.returned_model)}",
                  f"check = {_s(item.check)}"]  # fmt: skip
        if item.verify is not None:
            pairs = ", ".join(f"{k} = {_s(v)}" for k, v in item.verify.items())
            lines.append(f"verify = {{ {pairs} }}")
            lines.append(f"verify_quotes = {_s(item.verify_quotes)}")
        lines += [f"decision = {_s(item.decision)}", f"note = {_s(item.note)}"]
    return "\n".join(lines) + "\n"


def merge_write(path: Path, ticker: str, new_items: list[ReviewItem]) -> tuple[int, int]:
    """Append items whose id is new; existing items keep every field. Returns (added, kept)."""
    review = parse(path) if path.exists() else ExtractionReview(ticker)
    known = {i.id for i in review.items}
    added = [i for i in new_items if i.id not in known]
    review.items.extend(added)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(review), encoding="utf-8")
    return len(added), len(known)


def load_signed(directory: Path) -> list[tuple[Path, ExtractionReview]]:
    if not directory.exists():
        return []
    reviews = [(p, parse(p)) for p in sorted(directory.glob("*.toml"))]
    return [(p, r) for p, r in reviews if r.verified_by]
