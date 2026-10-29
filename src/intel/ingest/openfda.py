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
from intel.fetch import Throttled, read_fetched_at, request_record, write_cache
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
    "therapeutics",
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
    return {k for k in (key, base) if k}


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


# --- build step -----------------------------------------------------------------------


def ingest(ctx: BuildContext) -> None:
    apps = load_applications(ctx.inputs)
    path = cache_path(ctx.inputs)
    if apps is None:
        ctx.notes.append(f"openFDA cache missing at {path}; no approvals recorded")
        return
    by_core: dict[str, list[dict]] = defaultdict(list)
    for app in apps:
        by_core[sponsor_core(app["sponsor_name"] or "")].append(app)
    targets = {t.ticker: t for t in ctx.session.exec(select(Target)).all()}
    fetched_at = read_fetched_at(path)
    for company in candidate_pool(ctx.inputs):
        cores = {sponsor_core(a) for a in company.aliases}
        for app in (a for core in sorted(cores) for a in by_core.get(core, [])):
            approved = _approval_date(app)
            if approved is None:
                continue  # tentative or pending applications are not approvals
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
                target_id=targets[company.ticker].id,
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
