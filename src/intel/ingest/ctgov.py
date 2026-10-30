"""ClinicalTrials.gov API v2: trials, posted primary results, and the pipeline derived from them.

Trial values are facts sourced to the study page. Programs, indications and stages derived
from registrations are inferences: a registered phase is not the company's reported stage.
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from intel.enums import ClaimKind, Confidence, ProducedBy, SourceType, Stage
from intel.fetch import Throttled, read_fetched_at, request_record, run_batch, write_cache
from intel.ingest import BuildContext, Inputs
from intel.ingest.openfda import approved_ingredients, brand_ingredients, sponsor_core
from intel.ingest.pool import Company, candidate_pool, normalize_name
from intel.models import Program, ProgramIndication, Source, Target, Trial, TrialResult

STUDIES_URL = "https://clinicaltrials.gov/api/v2/studies"
STUDY_PAGE = "https://clinicaltrials.gov/study/{nct}"
SEARCH_FIELDS = ",".join(
    [
        "protocolSection.identificationModule",
        "protocolSection.statusModule",
        "protocolSection.sponsorCollaboratorsModule",
        "protocolSection.designModule",
        "protocolSection.conditionsModule",
        "protocolSection.armsInterventionsModule",
        "hasResults",
    ]
)
RESULT_FIELDS = "resultsSection.outcomeMeasuresModule"
RESULT_PHASES = {Stage.phase2, Stage.phase2_3, Stage.phase3}

PHASES = {
    frozenset({"EARLY_PHASE1"}): Stage.phase1,
    frozenset({"PHASE1"}): Stage.phase1,
    frozenset({"PHASE1", "PHASE2"}): Stage.phase1_2,
    frozenset({"PHASE2"}): Stage.phase2,
    frozenset({"PHASE2", "PHASE3"}): Stage.phase2_3,
    frozenset({"PHASE3"}): Stage.phase3,
    frozenset({"PHASE4"}): Stage.approved,  # post-marketing study implies an approval
}
STAGE_ORDER = [
    Stage.unknown,
    Stage.preclinical,
    Stage.phase1,
    Stage.phase1_2,
    Stage.phase2,
    Stage.phase2_3,
    Stage.phase3,
    Stage.filed,
    Stage.approved,
]
PROGRAM_TYPES = {"DRUG", "BIOLOGICAL", "GENETIC"}
NON_PROGRAM = re.compile(
    r"\b(placebos?|vehicle|saline|sham|standard of care|best supportive care|"
    r"soc|usual care|matching|no intervention)\b",
    re.I,
)
# Generic comparator or background-therapy names: a regimen class, not anyone's asset.
GENERIC_THERAPY = re.compile(
    r"\b(chemotherapy|chemo|corticosteroids?|steroid regimen|antibiotics?|"
    r"(investigator|physician)'?s? choice|best available (therapy|treatment)|"
    r"standard (of care|disease-directed|therapy)|immunomodulatory\b.*\btherapy|\bim\)? therapy|"
    r"rescue medication|"
    r"m?-?folf\w*|aromatase inhibitor therapy|immune effector cell therapy|"
    r"(regimen selection|treatment) phase group|"
    r"(licensed|commercial|eua or approved)\b.*\bvaccine|"
    r"^(seasonal |inactivated |egg-based |adjuvanted )*(quadrivalent )?influenza vaccine)",
    re.I,
)
NON_INDICATION = re.compile(r"\bhealthy\b", re.I)
DERIVED_NOTE = "由 CT.gov 登记推导；登记阶段不等于公司公告的研发阶段，可能含联用 / 对照药"
MAX_RESULT_CHARS = 1500


def search_cache(inputs: Inputs, ticker: str) -> Path:
    return inputs.raw_dir / "ctgov" / f"{ticker}.json"


def results_cache(inputs: Inputs, nct: str) -> Path:
    return inputs.raw_dir / "ctgov" / "results" / f"{nct}.json"


def wants_results(study: dict) -> bool:
    phases = study["protocolSection"].get("designModule", {}).get("phases")
    return bool(study.get("hasResults")) and map_phase(phases) in RESULT_PHASES


def lead_sponsor(study: dict) -> str:
    return study["protocolSection"]["sponsorCollaboratorsModule"]["leadSponsor"]["name"]


def nct_id(study: dict) -> str:
    return study["protocolSection"]["identificationModule"]["nctId"]


def matched_studies(studies: list[dict], company: Company) -> list[dict]:
    keys = company.alias_keys
    return [s for s in studies if normalize_name(lead_sponsor(s)) in keys]


# --- fetch ----------------------------------------------------------------------------


def _search(http: Throttled, alias: str) -> tuple[list[dict], list[dict]]:
    studies, requests, token = [], [], None
    while True:
        params = {"query.lead": alias, "pageSize": 1000, "fields": SEARCH_FIELDS}
        if token:
            params["pageToken"] = token
        resp = http.get(STUDIES_URL, params=params)
        resp.raise_for_status()
        requests.append(request_record(resp))
        body = resp.json()
        studies += body.get("studies", [])
        token = body.get("nextPageToken")
        if not token:
            return studies, requests


def _fetch_results(inputs: Inputs, http: Throttled, nct: str, refresh: bool) -> None:
    path = results_cache(inputs, nct)
    if path.exists() and not refresh:
        return
    resp = http.get(f"{STUDIES_URL}/{nct}", params={"fields": RESULT_FIELDS})
    resp.raise_for_status()
    measures = (
        resp.json()
        .get("resultsSection", {})
        .get("outcomeMeasuresModule", {})
        .get("outcomeMeasures")
        or []
    )
    primary = [m for m in measures if m.get("type") == "PRIMARY"]
    write_cache(path, {"nctId": nct, "primaryOutcomeMeasures": primary}, [request_record(resp)])


def fetch(inputs: Inputs, http: Throttled, companies: list[Company], refresh: bool = False):
    def one(company: Company) -> None:
        by_nct, requests = {}, []
        for alias in company.aliases:
            studies, reqs = _search(http, alias)
            requests += reqs
            by_nct.update((nct_id(s), s) for s in studies)
        studies = [by_nct[k] for k in sorted(by_nct)]
        for study in matched_studies(studies, company):
            if wants_results(study):
                _fetch_results(inputs, http, nct_id(study), refresh)
        write_cache(
            search_cache(inputs, company.ticker),
            {"aliases": list(company.aliases), "studies": studies},
            requests,
        )

    return run_batch(companies, lambda c: search_cache(inputs, c.ticker), one, refresh)


# --- build: trials --------------------------------------------------------------------


def map_phase(phases: list[str] | None) -> Stage:
    return PHASES.get(frozenset(phases or []), Stage.unknown)


def _design(design: dict) -> str | None:
    info = design.get("designInfo") or {}
    parts = [
        ("allocation", info.get("allocation")),
        ("model", info.get("interventionModel")),
        ("masking", (info.get("maskingInfo") or {}).get("masking")),
        ("purpose", info.get("primaryPurpose")),
    ]
    text = "; ".join(f"{k}={v}" for k, v in parts if v)
    return text or None


def _date(struct: dict | None) -> tuple[str | None, str | None]:
    struct = struct or {}
    return struct.get("date"), struct.get("type")


def _trial_values(study: dict) -> dict:
    p = study["protocolSection"]
    status, design = p.get("statusModule", {}), p.get("designModule", {})
    enrollment = design.get("enrollmentInfo") or {}
    interventions = p.get("armsInterventionsModule", {}).get("interventions") or []
    start, _ = _date(status.get("startDateStruct"))
    primary, primary_type = _date(status.get("primaryCompletionDateStruct"))
    completion, completion_type = _date(status.get("completionDateStruct"))
    return {
        "title": p["identificationModule"].get("briefTitle"),
        "phase": map_phase(design.get("phases")),
        "status": status.get("overallStatus"),
        "design": _design(design),
        "conditions": "; ".join(p.get("conditionsModule", {}).get("conditions") or []) or None,
        "interventions": "; ".join(f"{i.get('type')}: {i.get('name')}" for i in interventions)
        or None,
        "enrollment": enrollment.get("count"),
        "enrollment_type": enrollment.get("type"),
        "start_date": start,
        "primary_completion_date": primary,
        "primary_completion_type": primary_type,
        "completion_date": completion,
        "_completion_type": completion_type,
        "_updated": status.get("lastUpdatePostDateStruct", {}).get("date"),
    }


TYPE_OF = {
    "enrollment": "enrollment_type",
    "primary_completion_date": "primary_completion_type",
    "completion_date": "_completion_type",
}


def _register_study(ctx: BuildContext, study: dict, path: Path, values: dict) -> str:
    nct = nct_id(study)
    source_id = f"CTG-{nct}"
    if ctx.session.get(Source, source_id) is None:
        from intel.ingest.mnc import exact_date

        ctx.session.add(
            Source(
                source_id=source_id,
                source_type=SourceType.ctgov,
                url=STUDY_PAGE.format(nct=nct),
                title=values["title"],
                publisher=lead_sponsor(study),
                doc_kind="ClinicalTrials.gov 登记记录",
                published_date_text=values["_updated"],
                published_date=exact_date(values["_updated"]),
                fetched_at=read_fetched_at(path),
            )
        )
    return source_id


def _add_trial(ctx: BuildContext, target: Target, study: dict, path: Path) -> Trial:
    values = _trial_values(study)
    source_id = _register_study(ctx, study, path, values)
    trial = Trial(
        nct_id=nct_id(study),
        target_id=target.id,
        **{k: v for k, v in values.items() if not k.startswith("_")},
    )
    ctx.session.add(trial)
    ctx.session.flush()
    for fld in Trial.BUSINESS_FIELDS:
        value = getattr(trial, fld)
        if value is None:
            continue
        kind_of_value = values.get(TYPE_OF.get(fld, ""), None)
        note = "CT.gov 登记值"
        if kind_of_value == "ESTIMATED":
            note += "；预计值（ESTIMATED）"
        elif kind_of_value == "ACTUAL":
            note += "；实际值（ACTUAL）"
        ctx.claim("trial", trial.id, fld, value, source_id, produced_by=ProducedBy.api, note=note)
    return trial


# --- build: results -------------------------------------------------------------------


def _p_value(value: str | None) -> str | None:
    if not value:
        return None
    return f"p {value}" if value[0] in "<>=" else f"p = {value}"


def _summarize_measure(m: dict) -> tuple[str, str | None]:
    groups = {g["id"]: g.get("title", g["id"]) for g in m.get("groups", [])}
    unit = m.get("unitOfMeasure") or ""
    disp = m.get("dispersionType") or ""
    parts = []
    for cls in m.get("classes", []):
        label = cls.get("title")
        for cat in cls.get("categories", []):
            cat_label = " / ".join(x for x in (label, cat.get("title")) if x)
            for meas in cat.get("measurements", []):
                value = meas.get("value")
                spread = meas.get("spread")
                rng = (
                    f" [{meas['lowerLimit']}, {meas['upperLimit']}]"
                    if meas.get("lowerLimit") and meas.get("upperLimit")
                    else ""
                )
                extra = f" ({disp} {spread})" if spread else rng
                prefix = f"{cat_label}: " if cat_label else ""
                parts.append(
                    f"{prefix}{groups.get(meas['groupId'], meas['groupId'])} = {value}{extra}"
                )
    result = f"[{m.get('paramType', '')}, {unit}] " + "; ".join(parts)
    analyses = [
        ", ".join(
            x
            for x in (
                _p_value(a.get("pValue")),
                a.get("statisticalMethod"),
                f"{a.get('paramType')} {a['paramValue']}" if a.get("paramValue") else None,
            )
            if x
        )
        for a in m.get("analyses", [])
    ]
    analysis = "; ".join(a for a in analyses if a) or None
    return result[:MAX_RESULT_CHARS], analysis[:MAX_RESULT_CHARS] if analysis else None


def _add_results(ctx: BuildContext, trial: Trial, source_id: str) -> None:
    path = results_cache(ctx.inputs, trial.nct_id)
    if not path.exists():
        ctx.gap("trial", trial.nct_id, "results", "ctgov_results_cache_missing", str(path))
        return
    for m in json.loads(path.read_text())["primaryOutcomeMeasures"]:
        result, analysis = _summarize_measure(m)
        endpoint = m.get("title")
        if m.get("timeFrame"):
            endpoint = f"{endpoint}（{m['timeFrame']}）"
        row = TrialResult(trial_id=trial.id, endpoint=endpoint, result=result, analysis=analysis)
        ctx.session.add(row)
        ctx.session.flush()
        for fld in ("endpoint", "result", "analysis"):
            if getattr(row, fld):
                ctx.claim(
                    "trial_result",
                    row.id,
                    fld,
                    getattr(row, fld),
                    source_id,
                    produced_by=ProducedBy.api,
                    note="CT.gov 已发布结果的主要终点，按登记原文汇总",
                )


# --- build: derived pipeline ----------------------------------------------------------


def normalize_intervention(name: str) -> str:
    name = re.sub(r"\(.*?\)|\[.*?\]", " ", name)
    name = re.sub(r"\b\d+(\.\d+)?\s*(mg|µg|ug|mcg|g|ml|mg/kg|iu)\b", " ", name, flags=re.I)
    name = re.sub(
        r"\b(oral|tablets?|capsules?|injections?|infusion|subcutaneous|sc|iv|intravenous|"
        r"po|qd|bid|tid|high dose|low dose|dose|solution|suspension|drug)\b",
        " ",
        name,
        flags=re.I,
    )
    return " ".join(re.sub(r"[^\w\- ]+", " ", name).split()).strip(" -").upper()


def _manual_excludes(inputs: Inputs) -> set[str]:
    path = inputs.manual_dir / "intervention_excludes.csv"
    if not path.exists():
        return set()
    import csv

    with path.open(newline="", encoding="utf-8") as fh:
        return {normalize_intervention(r["name"]) for r in csv.DictReader(fh)}


def _code_prefixes(inputs: Inputs) -> list[tuple[re.Pattern, str]]:
    """Other companies' research-code prefixes ("PF-" -> Pfizer), from a manual file."""
    path = inputs.manual_dir / "sponsor_code_prefixes.csv"
    if not path.exists():
        return []
    import csv

    with path.open(newline="", encoding="utf-8") as fh:
        return [
            (re.compile(rf"^{re.escape(r['prefix'].strip())} ?-?\d"), sponsor_core(r["owner"]))
            for r in csv.DictReader(fh)
        ]


def _program_aliases(inputs: Inputs) -> dict[str, list[tuple[str, str]]]:
    """Ticker -> (name, same_as) pairs the registry never links (code name vs INN)."""
    path = inputs.manual_dir / "program_aliases.csv"
    out: dict[str, list[tuple[str, str]]] = defaultdict(list)
    if path.exists():
        import csv

        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                out[r["ticker"].strip()].append(
                    (normalize_intervention(r["name"]), normalize_intervention(r["same_as"]))
                )
    return out


@dataclass(frozen=True)
class ProgramFilter:
    """Decides which trial interventions are the sponsor's own programs."""

    excludes: set[str]  # manual exclusions
    approved: dict[str, set[str]]  # approved ingredient/brand key -> holder sponsor cores
    brands: dict[str, set[str]]  # brand key -> ingredient keys
    own: set[str]  # this company's sponsor cores
    prefixes: tuple[tuple[re.Pattern, str], ...] = ()  # other companies' code prefixes

    def is_foreign_code(self, key: str) -> bool:
        return any(rx.match(key) and owner not in self.own for rx, owner in self.prefixes)

    def is_program(self, key: str) -> bool:
        if not key or key in self.excludes:
            return False
        # Another company's marketed drug is a partner or comparator, not this sponsor's
        # program; check the whole name and each word ("ACTOS PIOGLITAZONE").
        for part in (key, *key.split()):
            holders = self.approved.get(part)
            if holders and not holders & self.own:
                return False
        return True


def _eligible_interventions(study: dict, keep: ProgramFilter) -> list[list[str]]:
    """Name keys (primary first, then other names) of each intervention that is a program."""
    out = []
    for i in study["protocolSection"].get("armsInterventionsModule", {}).get("interventions") or []:
        name = i.get("name", "")
        if (
            i.get("type") not in PROGRAM_TYPES
            or NON_PROGRAM.search(name)
            or GENERIC_THERAPY.search(name)
        ):
            continue
        primary = normalize_intervention(i["name"])
        if not keep.is_program(primary):
            continue
        others = [normalize_intervention(n) for n in i.get("otherNames") or []]
        keys = list(dict.fromkeys([primary, *(k for k in others if k)]))
        # A partner's coded compound ("PF-07220060") is theirs unless the registration also
        # names it with a code or INN of its own.
        if all(keep.is_foreign_code(k) for k in keys):
            continue
        out.append(keys)
    return out


class _Names:
    """Union-find over the names of one company's drugs (code name, INN, brand)."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.uses: dict[str, int] = defaultdict(int)

    def find(self, key: str) -> str:
        self.parent.setdefault(key, key)
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def union(self, a: str, b: str) -> None:
        self.parent[self.find(a)] = self.find(b)

    def label(self, key: str) -> str:
        """The cluster's most used primary name, with its other names in brackets."""
        root = self.find(key)
        members = [k for k in self.parent if self.find(k) == root]
        members.sort(key=lambda k: (-self.uses[k], any(c.isdigit() for c in k), k))
        head, rest = members[0], [m for m in members[1:] if self.uses[m]]
        return f"{head} ({', '.join(rest)})" if rest else head


def _indication(study: dict) -> str | None:
    """The first listed condition, which registrants use for the primary indication."""
    conditions = study["protocolSection"].get("conditionsModule", {}).get("conditions") or []
    for c in conditions:
        if c.strip() and not NON_INDICATION.search(c):
            return c.strip()
    return None


def _derive_pipeline(
    ctx: BuildContext,
    target: Target,
    studies: list[dict],
    trials: dict[str, Trial],
    keep: ProgramFilter,
    aliases: list[tuple[str, str]] = (),
) -> None:
    names = _Names()
    for name, same_as in aliases:
        names.union(name, same_as)
    per_study: dict[str, list[str]] = {}
    for study in studies:
        primaries = []
        for keys in _eligible_interventions(study, keep):
            names.uses[keys[0]] += 1
            for other in keys[1:]:
                names.union(keys[0], other)
            for ingredient in keep.brands.get(keys[0], ()):
                if ingredient in names.parent:
                    names.union(keys[0], ingredient)
            names.find(keys[0])
            primaries.append(keys[0])
        per_study[nct_id(study)] = primaries
    for brand, ingredients in keep.brands.items():  # brand seen before its ingredient
        if brand in names.parent:
            for ingredient in ingredients & names.parent.keys():
                names.union(brand, ingredient)

    stages: dict[tuple[str, str], list[tuple[Stage, str]]] = defaultdict(list)
    first_link: dict[str, tuple[str, str]] = {}
    for study in studies:
        nct = nct_id(study)
        stage = map_phase(study["protocolSection"]["designModule"].get("phases"))
        indication = _indication(study)
        programs = list(dict.fromkeys(names.label(k) for k in per_study[nct]))
        if not indication or not programs:
            continue
        for prog in programs:
            stages[(prog, indication)].append((stage, nct))
        first_link[nct] = (programs[0], indication)

    programs: dict[str, Program] = {}
    rows: dict[tuple[str, str], ProgramIndication] = {}
    for (prog, ind), found in sorted(stages.items()):
        if prog not in programs:
            programs[prog] = Program(target_id=target.id, name=prog)
            ctx.session.add(programs[prog])
            ctx.session.flush()
        best_stage, best_nct = max(found, key=lambda x: (STAGE_ORDER.index(x[0]), x[1]))
        row = ProgramIndication(program_id=programs[prog].id, indication=ind, stage=best_stage)
        ctx.session.add(row)
        ctx.session.flush()
        rows[(prog, ind)] = row
        for fld, value in (("indication", ind), ("stage", best_stage.value)):
            ctx.claim(
                "program_indication",
                row.id,
                fld,
                value,
                f"CTG-{best_nct}",
                kind=ClaimKind.inference,
                confidence=Confidence.medium,
                produced_by=ProducedBy.api,
                note=f"{DERIVED_NOTE}；依据 {len(found)} 项试验",
            )
    for nct, key in first_link.items():
        trials[nct].indication_id = rows[key].id


# --- build step -----------------------------------------------------------------------


def ingest(ctx: BuildContext) -> None:
    from sqlmodel import select

    targets = {t.ticker: t for t in ctx.session.exec(select(Target)).all()}
    excludes = _manual_excludes(ctx.inputs)
    prefixes = tuple(_code_prefixes(ctx.inputs))
    program_aliases = _program_aliases(ctx.inputs)
    approved = approved_ingredients(ctx.inputs)
    brands = brand_ingredients(ctx.inputs)
    seen: set[str] = set()
    for company in candidate_pool(ctx.inputs):
        target = targets[company.ticker]
        path = search_cache(ctx.inputs, company.ticker)
        if not path.exists():
            ctx.gap("target", company.ticker, "trials", "ctgov_cache_missing", str(path))
            continue
        studies = matched_studies(json.loads(path.read_text())["studies"], company)
        studies = [s for s in studies if nct_id(s) not in seen]
        if not studies:
            ctx.gap(
                "target",
                company.ticker,
                "trials",
                "no_lead_sponsor_match",
                f"aliases: {' | '.join(company.aliases)}",
            )
            continue
        trials = {}
        for study in studies:
            seen.add(nct_id(study))
            trial = _add_trial(ctx, target, study, path)
            trials[trial.nct_id] = trial
            if wants_results(study):
                _add_results(ctx, trial, f"CTG-{trial.nct_id}")
        own = {sponsor_core(a) for a in company.aliases}
        _derive_pipeline(
            ctx,
            target,
            studies,
            trials,
            ProgramFilter(excludes, approved, brands, own, prefixes),
            program_aliases.get(company.ticker, []),
        )
