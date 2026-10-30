"""openFDA drugsfda: approved products per candidate, and the set of approved ingredients.

The bulk export is fetched once and trimmed to NDA/BLA applications. Besides recording each
candidate's approvals, it tells the pipeline derivation which trial interventions are other
companies' marketed drugs (combination partners or comparators, not the sponsor's programs).
"""

import io
import json
import re
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

from sqlmodel import select

from intel.enums import ProducedBy, SourceType
from intel.fetch import BatchResult, Throttled, read_fetched_at, request_record, write_cache
from intel.ingest import BuildContext, Inputs
from intel.ingest.pool import candidate_pool, normalize_name
from intel.models import ApprovedProduct, Source, Target

DOWNLOAD_INDEX = "https://api.fda.gov/download.json"
APPLICATION_PAGE = (
    "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo={no}"
)
# Trailing words that openFDA sponsor names usually omit ("MADRIGAL" vs "Madrigal Pharmaceuticals").
GENERIC_TAIL = {
    "pharmaceuticals",
    "pharmaceutical",
    "pharma",
    "pharms",  # openFDA abbreviations: "ACADIA PHARMS", "BIOMARIN PHARM", "PRIOVANT THERAP"
    "pharm",
    "therapeutics",
    "theraps",
    "therap",
    "operation",  # "ARS PHARMS OPERATION"
    "biosciences",
    "bioscience",
    "biopharma",
    "biotherapeutics",
    "biotechnology",
    "biologics",
    "bio",
    "sciences",
    "medicines",
    "life",
    "us",
    "usa",
}


def cache_path(inputs: Inputs) -> Path:
    return inputs.raw_dir / "openfda" / "drugsfda_nda_bla.json"


def sponsor_core(name: str) -> str:
    words = normalize_name(name).split()
    while len(words) > 1 and words[-1] in GENERIC_TAIL:
        words.pop()
    return " ".join(words)


SALT_WORDS = {
    "ACETATE",
    "BESYLATE",
    "BROMIDE",
    "CALCIUM",
    "CHLORIDE",
    "CITRATE",
    "DIHYDROCHLORIDE",
    "DISODIUM",
    "FUMARATE",
    "HEMIHYDRATE",
    "HYDROBROMIDE",
    "HYDROCHLORIDE",
    "MALATE",
    "MALEATE",
    "MESYLATE",
    "MONOHYDRATE",
    "PHOSPHATE",
    "POTASSIUM",
    "SODIUM",
    "SUCCINATE",
    "SULFATE",
    "TARTRATE",
    "TOSYLATE",
    "DIMESYLATE",
    "HYDRATE",
    "ANHYDROUS",
}


def ingredient_key(name: str) -> str:
    return " ".join(re.sub(r"[^\w\- ]+", " ", name).split()).upper()


def ingredient_keys(name: str) -> set[str]:
    """The ingredient as listed, plus its base form without salt words."""
    key = ingredient_key(name)
    base = " ".join(w for w in key.split() if w not in SALT_WORDS)
    # Biologics carry a four-letter FDA suffix ("TIVIDENOFUSP ALFA-EKNM"); trials use the core.
    core = re.sub(r"-[A-Z]{4}$", "", base)
    return {k for k in (key, base, core) if k}


# --- fetch ----------------------------------------------------------------------------


def _trim(app: dict) -> dict:
    return {
        "application_number": app.get("application_number"),
        "sponsor_name": app.get("sponsor_name"),
        "products": [
            {
                "brand_name": p.get("brand_name"),
                "active_ingredients": [a.get("name") for a in p.get("active_ingredients") or []],
                "marketing_status": p.get("marketing_status"),
            }
            for p in app.get("products") or []
        ],
        "submissions": [
            {
                "submission_type": s.get("submission_type"),
                "submission_status": s.get("submission_status"),
                "submission_status_date": s.get("submission_status_date"),
            }
            for s in app.get("submissions") or []
            if s.get("submission_type") == "ORIG"
        ],
    }


def fetch(inputs: Inputs, http: Throttled) -> Path:
    index = http.get(DOWNLOAD_INDEX)
    index.raise_for_status()
    part = index.json()["results"]["drug"]["drugsfda"]["partitions"][0]["file"]
    resp = http.get(part)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        data = json.loads(zf.read(zf.namelist()[0]))
    apps = [
        _trim(a)
        for a in data["results"]
        if str(a.get("application_number", "")).startswith(("NDA", "BLA"))
    ]
    apps.sort(key=lambda a: a["application_number"])
    path = cache_path(inputs)
    write_cache(
        path,
        {"export_date": data.get("meta", {}).get("last_updated"), "applications": apps},
        [request_record(index), request_record(resp)],
    )
    return path


# --- shared lookups -------------------------------------------------------------------


def load_applications(inputs: Inputs) -> list[dict] | None:
    path = cache_path(inputs)
    return json.loads(path.read_text())["applications"] if path.exists() else None


def approved_ingredients(inputs: Inputs) -> dict[str, set[str]]:
    """Ingredient or brand key -> sponsor cores holding an NDA/BLA for it."""
    out: dict[str, set[str]] = defaultdict(set)
    for app in load_applications(inputs) or []:
        core = sponsor_core(app["sponsor_name"] or "")
        for product in app["products"]:
            for name in [product["brand_name"], *product["active_ingredients"]]:
                for key in ingredient_keys(name or ""):
                    out[key].add(core)
    return out


def brand_ingredients(inputs: Inputs) -> dict[str, set[str]]:
    """Brand key -> base ingredient keys, to merge a brand with its INN."""
    out: dict[str, set[str]] = defaultdict(set)
    for app in load_applications(inputs) or []:
        for product in app["products"]:
            if product["brand_name"]:
                for name in product["active_ingredients"]:
                    out[ingredient_key(product["brand_name"])] |= ingredient_keys(name or "")
    return out


def _approval_date(app: dict) -> date | None:
    dates = [
        s["submission_status_date"]
        for s in app["submissions"]
        if s["submission_status"] == "AP" and s["submission_status_date"]
    ]
    if not dates:
        return None
    d = min(dates)
    return date(int(d[:4]), int(d[4:6]), int(d[6:8]))


def candidate_approvals(inputs: Inputs, apps: list[dict]) -> dict[str, list[dict]]:
    """Ticker -> approved NDA/BLA applications held under one of the company's names."""
    by_core: dict[str, list[dict]] = defaultdict(list)
    for app in apps:
        if _approval_date(app):  # tentative or pending applications are not approvals
            by_core[sponsor_core(app["sponsor_name"] or "")].append(app)
    out = {}
    for company in candidate_pool(inputs):
        cores = sorted({sponsor_core(a) for a in company.aliases})
        owned = [a for core in cores for a in by_core.get(core, [])]
        if owned:
            out[company.ticker] = owned
    return out


# --- labels ---------------------------------------------------------------------------

LABEL_URL = "https://api.fda.gov/drug/label.json"


def label_cache(inputs: Inputs, number: str) -> Path:
    return inputs.raw_dir / "openfda" / "labels" / f"{number}.json"


def fetch_labels(inputs: Inputs, http: Throttled, refresh: bool = False) -> BatchResult:
    """The current label's indications for every candidate approval (one query each)."""
    result = BatchResult()
    for ticker, owned in sorted(
        candidate_approvals(inputs, load_applications(inputs) or []).items()
    ):
        for app in owned:
            number = app["application_number"]
            path = label_cache(inputs, number)
            if path.exists() and not refresh:
                result.skipped.append(number)
                continue
            resp = http.get(
                LABEL_URL,
                params={"search": f'openfda.application_number:"{number}"', "limit": 1},
            )
            if resp.status_code == 404:  # openFDA answers "no matches" with 404
                label = None
            elif resp.status_code != 200:
                result.failed[number] = f"{ticker}: HTTP {resp.status_code}"
                continue
            else:
                hit = resp.json()["results"][0]
                label = {
                    "set_id": hit.get("set_id"),
                    "effective_time": hit.get("effective_time"),
                    "indications_and_usage": " ".join(hit.get("indications_and_usage") or []),
                }
            write_cache(
                path, {"application_number": number, "label": label}, [request_record(resp)]
            )
            result.fetched.append(number)
    return result


STOP_WORDS = {"and", "or", "of", "the", "in", "with", "a", "an", "to", "for", "disease", "adult"}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def label_covers(indication: str, label_text: str) -> bool:
    """Every content word of the trial indication appears in the label's indications."""
    wanted = [w for w in _words(indication) if w not in STOP_WORDS]
    have = set(_words(label_text))
    return bool(wanted) and all(w in have or w.rstrip("s") in have for w in wanted)


# --- build step -----------------------------------------------------------------------


def ingest(ctx: BuildContext) -> None:
    apps = load_applications(ctx.inputs)
    path = cache_path(ctx.inputs)
    if apps is None:
        ctx.notes.append(f"openFDA cache missing at {path}; no approvals recorded")
        return
    targets = {t.ticker: t for t in ctx.session.exec(select(Target)).all()}
    fetched_at = read_fetched_at(path)
    for ticker, owned in candidate_approvals(ctx.inputs, apps).items():
        for app in owned:
            approved = _approval_date(app)
            number = app["application_number"]
            source_id = f"FDA-{number}"
            ctx.session.add(
                Source(
                    source_id=source_id,
                    source_type=SourceType.openfda,
                    url=APPLICATION_PAGE.format(no=re.sub(r"\D", "", number)),
                    title=f"Drugs@FDA {number}",
                    publisher=app["sponsor_name"],
                    doc_kind="openFDA drugsfda 申请记录",
                    fetched_at=fetched_at,
                    local_path=str(path),
                )
            )
            ctx.session.flush()
            products = app["products"]
            row = ApprovedProduct(
                target_id=targets[ticker].id,
                application_number=number,
                brand_name="; ".join(
                    dict.fromkeys(p["brand_name"] for p in products if p["brand_name"])
                )
                or None,
                active_ingredients="; ".join(
                    dict.fromkeys(a for p in products for a in p["active_ingredients"] if a)
                )
                or None,
                first_approval_date=approved,
            )
            ctx.session.add(row)
            ctx.session.flush()
            for fld in ApprovedProduct.BUSINESS_FIELDS:
                if getattr(row, fld) is not None:
                    ctx.claim(
                        "approved_product",
                        row.id,
                        fld,
                        getattr(row, fld),
                        source_id,
                        produced_by=ProducedBy.api,
                        note=f"openFDA sponsor_name: {app['sponsor_name']}",
                    )


def approved_stage(ctx: BuildContext) -> None:
    """Raise a derived indication to approved when its own FDA label lists it.

    The pipeline is derived from trial registrations, so an approved asset otherwise keeps
    its last trial phase. Runs after the CT.gov step.
    """
    from intel.enums import ClaimKind, Confidence, Stage
    from intel.models import Claim

    for target in ctx.session.exec(select(Target)).all():
        for product in target.approvals:
            path = label_cache(ctx.inputs, product.application_number)
            if not path.exists():
                continue
            data = json.loads(path.read_text())
            label = data["label"]
            if not label or not label["indications_and_usage"]:
                continue
            source_id = f"FDA-LABEL-{product.application_number}"
            names = [product.brand_name or "", *(product.active_ingredients or "").split("; ")]
            keys = {k for n in names for k in ingredient_keys(n) if len(k) > 3}
            for program in target.programs:
                if not any(re.search(rf"\b{re.escape(k)}\b", program.name) for k in keys):
                    continue
                for pi in program.indications:
                    if pi.stage == Stage.approved or not label_covers(
                        pi.indication or "", label["indications_and_usage"]
                    ):
                        continue
                    if ctx.session.get(Source, source_id) is None:
                        ctx.session.add(
                            Source(
                                source_id=source_id,
                                source_type=SourceType.fda_web,
                                url=f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={label['set_id']}",
                                title=f"FDA label {product.application_number}",
                                publisher="U.S. FDA (openFDA drug label)",
                                doc_kind="药品说明书适应症（openFDA drug label）",
                                fetched_at=read_fetched_at(path),
                                local_path=str(path),
                            )
                        )
                        ctx.session.flush()
                    for old in ctx.session.exec(
                        select(Claim).where(
                            Claim.entity_type == "program_indication",
                            Claim.entity_id == str(pi.id),
                            Claim.field == "stage",
                        )
                    ).all():
                        ctx.session.delete(old)
                    pi.stage = Stage.approved
                    ctx.session.add(pi)
                    ctx.claim(
                        "program_indication",
                        pi.id,
                        "stage",
                        Stage.approved.value,
                        source_id,
                        kind=ClaimKind.inference,
                        confidence=Confidence.medium_high,
                        produced_by=ProducedBy.api,
                        note=(
                            f"{product.application_number} 说明书适应症包含该适应症全部关键词；"
                            f"资产名含 {', '.join(sorted(k for k in keys if k in program.name))}"
                        ),
                    )
    ctx.session.flush()
