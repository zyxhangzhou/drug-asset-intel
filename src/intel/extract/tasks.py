"""The three extraction item types: fields, retrieval queries and prompts."""

import json
from dataclasses import dataclass

from intel.enums import CatalystType, Confidence


@dataclass(frozen=True)
class Task:
    name: str
    fields: tuple[str, ...]  # value fields the model fills, besides "quotes"
    required: tuple[str, ...]  # an item without these is rejected
    query: str  # FTS5 query choosing the chunks sent to the model
    instruction: str


TASKS = {
    t.name: t
    for t in (
        Task(
            name="program",
            fields=("asset", "mechanism", "modality"),
            required=("asset",),
            query=(
                'mechanism OR inhibitor OR agonist OR antagonist OR antibody OR "small molecule" '
                'OR sirna OR rnai OR "gene therapy" OR "cell therapy" OR conjugate OR degrader '
                "OR targeting OR selective OR designed"
            ),
            instruction=(
                "For each drug candidate of the company named in the text, give its mechanism of "
                "action (e.g. 'dual GLP-1/GIP receptor agonist') and modality (e.g. small "
                "molecule, peptide, monoclonal antibody, ADC, AAV gene therapy, siRNA, cell "
                "therapy), worded as the text words them. Modality is the drug class, not the "
                "route of administration: 'oral' or 'subcutaneous' is not a modality."
            ),
        ),
        Task(
            name="clinical_result",
            fields=(
                "asset",
                "trial",
                "indication",
                "endpoint",
                "result",
                "analysis",
                "comparator",
                "advantage_vs_soc",
            ),
            required=("asset", "endpoint", "result"),
            query=(
                '"primary endpoint" OR "secondary endpoint" OR placebo OR topline OR '
                '"statistically significant" OR efficacy OR response OR reduction OR '
                "improvement OR met OR achieved OR baseline OR week"
            ),
            instruction=(
                "For each reported clinical result of the company's own drug candidates, give: "
                "trial (NCT number, or the trial name used in the text), indication, endpoint "
                "(with the time point), result (the numbers as reported, per arm or dose), "
                "analysis (p-value, confidence interval or statistical test, only if stated), "
                "comparator (placebo, active drug, or none). Fill advantage_vs_soc only when the "
                "text itself compares the candidate with the standard of care or an approved "
                "therapy; then also set confidence to one of high, medium_high, medium, low. "
                "Skip preclinical results and results of other companies' drugs. "
                "One item per endpoint of a trial: a text reporting response rate and survival "
                "gives two items; all arms or doses of one endpoint stay in that one item. Write "
                "a time point (e.g. week 52) only when a quote states it: if it is in another "
                "sentence, quote that sentence as well; otherwise leave the time point out."
            ),
        ),
        Task(
            name="catalyst",
            fields=("asset", "event", "event_type", "timing"),
            required=("event", "event_type", "timing"),
            query=(
                "expect OR expected OR anticipate OR anticipated OR plan OR planned OR "
                "milestone OR milestones OR readout OR initiate OR submission OR submit OR "
                'pdufa OR guidance OR quarter OR half OR "year-end"'
            ),
            instruction=(
                "List future events the company says will happen: data readouts, regulatory "
                "submissions, regulatory decisions (e.g. PDUFA dates), trial starts. event_type "
                f"is one of {', '.join(t.value for t in CatalystType)}. timing is the time "
                "expression exactly as written (e.g. 'second half of 2027', 'Q1 2027'). Skip "
                "events whose timing has no year, and events already completed."
            ),
        ),
    )
}

NUMBER_CHECKED = (
    "mechanism",
    "modality",
    "indication",
    "endpoint",
    "result",
    "analysis",
    "comparator",
    "advantage_vs_soc",
    "event",
    "timing",
)

SYSTEM_PROMPT = """You extract facts from biotech company documents for an investment database.
Rules:
- Use only the document text you are given. Never add knowledge from memory.
- Every item carries "quotes": snippets copied verbatim from the text (exact words and \
characters, at least 20 characters each). Together the quotes must contain every number that \
appears in any field of the item: values, time points (e.g. week 21), doses and units. When a \
number comes from a table header, column label or section heading, quote that line as well.
- Tables are also given as table records, one line per cell: \
"[table N] <title> — <row> | <column>: <value>". For values from a table, quote the table record \
line of every cell you use, one quote per line, with no limit on the number of quotes: each line \
already carries the title, dose and time point. For running text, 1 to 4 quotes are enough.
- If the text does not state a field, leave it as an empty string. Do not guess, round or \
convert units.
- Reply with one JSON object: {"items": [...]}. Return {"items": []} when nothing qualifies."""


def user_prompt(task: Task, ticker: str, programs: list[str], chunks: list) -> str:
    example = {f: "" for f in task.fields} | {"quotes": ["..."]}
    if task.name == "clinical_result":
        example["confidence"] = ""
    parts = [
        f"Company ticker: {ticker}.",
        f"Known program names of this company (use one when it is the same drug): "
        f"{', '.join(programs) or 'none listed'}.",
        f"Task: {task.instruction}",
        f"Item format: {json.dumps(example)}",
        "Document excerpts:",
    ]
    for c in chunks:
        parts.append(f"[excerpt {c.no}]\n{c.text}")
    return "\n\n".join(parts)


CONFIDENCE_VALUES = {c.value for c in Confidence}
