import io
import json
import re
import shutil
import zipfile
from pathlib import Path

import httpx
import pytest
from sqlmodel import Session, select

from intel.build import build_snapshot
from intel.db import rw_engine
from intel.enums import ClaimKind, Stage
from intel.fetch import Throttled, meta_path, write_cache
from intel.ingest import Inputs, ctgov, openfda
from intel.models import (
    ApprovedProduct,
    Claim,
    Program,
    ProgramIndication,
    Source,
    Target,
    Trial,
    TrialResult,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def study(nct, sponsor, phases, interventions, conditions, *, status="RECRUITING", results=False):
    return {
        "hasResults": results,
        "protocolSection": {
            "identificationModule": {"nctId": nct, "briefTitle": f"Study {nct}"},
            "statusModule": {
                "overallStatus": status,
                "startDateStruct": {"date": "2025-03"},
                "primaryCompletionDateStruct": {"date": "2027-07-01", "type": "ESTIMATED"},
                "lastUpdatePostDateStruct": {"date": "2026-09-01"},
            },
            "sponsorCollaboratorsModule": {"leadSponsor": {"name": sponsor}},
            "designModule": {
                "phases": phases,
                "enrollmentInfo": {"count": 100, "type": "ESTIMATED"},
                "designInfo": {"allocation": "RANDOMIZED", "primaryPurpose": "TREATMENT"},
            },
            "conditionsModule": {"conditions": conditions},
            "armsInterventionsModule": {
                "interventions": [
                    {"type": t, "name": n, **({"otherNames": o} if o else {})}
                    for t, n, o in interventions
                ]
            },
        },
    }


def raw_with(tmp: Path, extra: dict[str, list[dict]] | None = None) -> Path:
    raw = tmp / "raw"
    shutil.copytree(FIXTURES / "ctgov", raw / "ctgov")
    shutil.copytree(FIXTURES / "openfda", raw / "openfda")
    for ticker, studies in (extra or {}).items():
        (raw / "ctgov" / f"{ticker}.json").write_text(json.dumps({"studies": studies}))
        meta_path(raw / "ctgov" / f"{ticker}.json").write_text(
            json.dumps({"fetched_at": "2026-10-29T00:00:00+00:00", "requests": []})
        )
    return raw


VIKING = "Viking Therapeutics, Inc."
SYNTHETIC = [
    study("NCT90000001", VIKING, ["PHASE2"], [("DRUG", "VK2735", None)], ["Obesity"]),
    study(
        "NCT90000002",
        VIKING,
        ["PHASE3"],
        [("DRUG", "VK2735 Oral Tablet", None), ("DRUG", "Placebos", None)],
        ["Obesity"],
    ),
    study("NCT90000003", "Some Other Pharma", ["PHASE1"], [("DRUG", "X-1", None)], ["Obesity"]),
]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("ctgov")
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment",
        raw_dir=raw_with(tmp, {"VKTX": SYNTHETIC}),
        manual_dir=tmp / "manual",
    )
    db = tmp / "intel.db"
    report = build_snapshot(db, inputs)
    return db, report


@pytest.fixture
def s(built):
    with Session(rw_engine(built[0])) as session:
        yield session


def target(s, ticker):
    return s.exec(select(Target).where(Target.ticker == ticker)).one()


def programs(s, ticker):
    return {
        p.name for p in s.exec(select(Program).where(Program.target_id == target(s, ticker).id))
    }


# --- sponsor matching -----------------------------------------------------------------


def test_text_search_false_positive_is_dropped(s):
    ncts = {t.nct_id for t in target(s, "VKTX").trials}
    assert ncts == {"NCT90000001", "NCT90000002"}
    assert s.exec(select(Trial).where(Trial.nct_id == "NCT90000003")).first() is None


def test_real_fixture_trials_match_lead_sponsor(s):
    cached = json.loads((FIXTURES / "ctgov" / "RLAY.json").read_text())["studies"]
    relay = {ctgov.nct_id(x) for x in cached if "relay" in ctgov.lead_sponsor(x).lower()}
    assert {t.nct_id for t in target(s, "RLAY").trials} == relay and relay


def test_company_without_cache_or_match_is_a_gap(built):
    reasons = {(g.key, g.reason) for g in built[1].gaps}
    assert ("BEAM", "ctgov_cache_missing") in reasons


def test_no_match_gap(tmp_path):
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment",
        raw_dir=raw_with(tmp_path, {"VKTX": [SYNTHETIC[2]]}),
        manual_dir=tmp_path / "manual",
    )
    report = build_snapshot(tmp_path / "x.db", inputs)
    assert any(g.key == "VKTX" and g.reason == "no_lead_sponsor_match" for g in report.gaps)


# --- trial facts ----------------------------------------------------------------------


def test_estimated_completion_is_labelled_and_readout_empty(s):
    trial = s.exec(select(Trial).where(Trial.nct_id == "NCT90000001")).one()
    assert (trial.primary_completion_date, trial.primary_completion_type) == (
        "2027-07-01",
        "ESTIMATED",
    )
    assert trial.start_date == "2025-03"  # month-precision dates are not padded
    assert trial.expected_readout is None
    (c,) = s.exec(
        select(Claim).where(
            Claim.entity_type == "trial",
            Claim.entity_id == str(trial.id),
            Claim.field == "primary_completion_date",
        )
    ).all()
    assert "ESTIMATED" in c.note and c.source_id == "CTG-NCT90000001" and c.kind == ClaimKind.fact
    assert s.get(Source, "CTG-NCT90000001").url == "https://clinicaltrials.gov/study/NCT90000001"


@pytest.mark.parametrize(
    ("phases", "stage"),
    [
        (["EARLY_PHASE1"], Stage.phase1),
        (["PHASE1", "PHASE2"], Stage.phase1_2),
        (["PHASE2", "PHASE3"], Stage.phase2_3),
        (["PHASE4"], Stage.approved),
        (["NA"], Stage.unknown),
        (None, Stage.unknown),
    ],
)
def test_phase_mapping(phases, stage):
    assert ctgov.map_phase(phases) == stage


# --- results --------------------------------------------------------------------------


def test_primary_outcome_captured(s):
    trial = s.exec(select(Trial).where(Trial.nct_id == "NCT02912260")).one()
    fixture = json.loads((FIXTURES / "ctgov" / "results" / "NCT02912260.json").read_text())
    measures = fixture["primaryOutcomeMeasures"]
    rows = s.exec(select(TrialResult).where(TrialResult.trial_id == trial.id)).all()
    assert len(rows) == len(measures)
    first = measures[0]
    assert rows[0].endpoint.startswith(first["title"])
    value = first["classes"][0]["categories"][0]["measurements"][0]["value"]
    assert value in rows[0].result


# --- derived pipeline -----------------------------------------------------------------


def test_highest_registered_phase_wins_and_placebo_is_dropped(s):
    names = programs(s, "VKTX")
    assert names == {"VK2735"}
    (row,) = s.exec(
        select(ProgramIndication).join(Program).where(Program.target_id == target(s, "VKTX").id)
    ).all()
    assert row.stage == Stage.phase3
    (c,) = s.exec(
        select(Claim).where(
            Claim.entity_type == "program_indication",
            Claim.entity_id == str(row.id),
            Claim.field == "stage",
        )
    ).all()
    assert c.kind == ClaimKind.inference and "CT.gov" in c.note


def test_other_companies_marketed_drug_is_not_a_program(s):
    names = programs(s, "RLAY")
    assert not any("FULVESTRANT" in n or "RIBOCICLIB" in n for n in names)
    assert any("RLY-2608" in n for n in names)


def test_code_name_and_inn_are_one_program(s):
    names = [n for n in programs(s, "MDGL") if "RESMETIROM" in n]
    assert len(names) == 1 and "MGL-3196" in names[0]


# --- openFDA --------------------------------------------------------------------------


def test_approved_product_recorded(s):
    (product,) = s.exec(
        select(ApprovedProduct).where(ApprovedProduct.target_id == target(s, "MDGL").id)
    ).all()
    assert (product.application_number, product.brand_name) == ("NDA217785", "REZDIFFRA")
    assert s.get(Source, "FDA-NDA217785").url.endswith("ApplNo=217785")


def test_company_without_approvals_is_fine(s):
    assert target(s, "VKTX").approvals == []


def test_salt_form_matches_base_ingredient():
    assert "RIBOCICLIB" in openfda.ingredient_keys("RIBOCICLIB SUCCINATE")
    assert "TIVIDENOFUSP ALFA" in openfda.ingredient_keys("TIVIDENOFUSP ALFA-EKNM")
    assert openfda.sponsor_core("Madrigal Pharmaceuticals, Inc.") == "madrigal"


@pytest.mark.parametrize(
    ("fda", "company"),
    [
        ("PRIOVANT THERAP", "Priovant Therapeutics"),
        ("ACADIA PHARMS", "ACADIA Pharmaceuticals Inc."),
        ("BIOMARIN PHARM", "BioMarin Pharmaceutical Inc."),
        ("SAREPTA THERAPS", "Sarepta Therapeutics, Inc."),
        ("ARS PHARMS OPERATION", "ARS Pharmaceuticals, Inc."),
    ],
)
def test_abbreviated_fda_sponsor_matches_company(fda, company):
    assert openfda.sponsor_core(fda) == openfda.sponsor_core(company)


def test_openfda_fetch_keeps_nda_bla_only(tmp_path):
    export = {
        "meta": {"last_updated": "2026-10-28"},
        "results": [
            {
                "application_number": "NDA000001",
                "sponsor_name": "A",
                "products": [],
                "submissions": [],
            },
            {
                "application_number": "ANDA000002",
                "sponsor_name": "B",
                "products": [],
                "submissions": [],
            },
        ],
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("drugsfda.json", json.dumps(export))

    def handler(request):
        if request.url.path == "/download.json":
            files = [{"file": "https://download.example/drugsfda.zip"}]
            return httpx.Response(
                200, json={"results": {"drug": {"drugsfda": {"partitions": files}}}}
            )
        return httpx.Response(200, content=buf.getvalue())

    http = Throttled(httpx.Client(transport=httpx.MockTransport(handler)), delay=0)
    path = openfda.fetch(Inputs(raw_dir=tmp_path), http)
    apps = json.loads(path.read_text())["applications"]
    assert [a["application_number"] for a in apps] == ["NDA000001"]
    assert len(json.loads(meta_path(path).read_text())["requests"]) == 2


# --- fetch ----------------------------------------------------------------------------


def test_ctgov_fetch_paginates_and_dedupes(tmp_path):
    pages = {
        None: {"studies": [SYNTHETIC[0]], "nextPageToken": "p2"},
        "p2": {"studies": [SYNTHETIC[0], SYNTHETIC[1]]},
    }

    def handler(request):
        return httpx.Response(200, json=pages[request.url.params.get("pageToken")])

    from intel.ingest.pool import Company

    company = Company("VKTX", VIKING, None, ("Viking Therapeutics",))
    http = Throttled(httpx.Client(transport=httpx.MockTransport(handler)), delay=0)
    inputs = Inputs(raw_dir=tmp_path)
    result = ctgov.fetch(inputs, http, [company])
    assert result.fetched == ["VKTX"]
    cached = json.loads(ctgov.search_cache(inputs, "VKTX").read_text())
    assert [ctgov.nct_id(x) for x in cached["studies"]] == ["NCT90000001", "NCT90000002"]
    assert (
        len(json.loads(meta_path(ctgov.search_cache(inputs, "VKTX")).read_text())["requests"]) == 2
    )


@pytest.mark.parametrize(
    ("name", "generic"),
    [
        ("Corticosteroids", True),
        ("Best Available Therapy", True),
        ("Investigator's Choice Treatment", True),
        ("Adjuvant Immunomodulatory (IM) Therapy", True),
        ("Licensed Seasonal Influenza Vaccine", True),
        ("mFOLFOX6 Regimen", True),
        ("VK2735", False),
        ("mRNA-1010", False),
        ("Pembrolizumab", False),
    ],
)
def test_generic_therapy_is_not_a_program(name, generic):
    assert bool(ctgov.GENERIC_THERAPY.search(name)) is generic


def test_dosing_words_do_not_split_a_program():
    assert ctgov.normalize_intervention("Brepocitinib PO QD") == "BREPOCITINIB"
    assert ctgov.normalize_intervention("Oral Brepocitinib") == "BREPOCITINIB"


def test_partner_code_is_not_own_program_unless_own_prefix():
    prefixes = ((re.compile(r"^PF- ?-?\d"), "pfizer"), (re.compile(r"^INCB ?-?\d"), "incyte"))
    keep = ctgov.ProgramFilter(set(), {}, {}, {"relay"}, prefixes)
    assert keep.is_foreign_code("PF-07220060")
    assert not keep.is_foreign_code("RLY-2608")
    incyte = ctgov.ProgramFilter(set(), {}, {}, {"incyte"}, prefixes)
    assert not incyte.is_foreign_code("INCB123667")


def test_label_covers_trial_indication():
    text = "AVLAYAH is indicated for Hunter syndrome (Mucopolysaccharidosis type II, MPS II)"
    assert openfda.label_covers("Mucopolysaccharidosis II", text)
    assert not openfda.label_covers("Myelofibrosis", text)
    assert openfda.label_covers("Myelodysplastic Syndromes", "lower-risk myelodysplastic syndrome")


def test_label_marks_listed_indication_approved(tmp_path):
    raw = raw_with(tmp_path)
    label = openfda.label_cache(Inputs(raw_dir=raw), "NDA217785")
    write_cache(
        label,
        {
            "application_number": "NDA217785",
            "label": {
                "set_id": "x",
                "effective_time": "20260101",
                "matched_by": "application_number",
                "indications_and_usage": "REZDIFFRA is indicated for noncirrhotic nonalcoholic "
                "steatohepatitis (NASH) with moderate to advanced liver fibrosis",
            },
        },
        [],
    )
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment", raw_dir=raw, manual_dir=tmp_path / "m"
    )
    build_snapshot(tmp_path / "intel.db", inputs)
    with Session(rw_engine(tmp_path / "intel.db")) as s:
        rows = {
            pi.indication: pi
            for p in target(s, "MDGL").programs
            if "RESMETIROM" in p.name
            for pi in p.indications
        }
        nash = rows["NASH - Nonalcoholic Steatohepatitis"]
        assert nash.stage == Stage.approved
        (c,) = s.exec(
            select(Claim).where(
                Claim.entity_type == "program_indication",
                Claim.entity_id == str(nash.id),
                Claim.field == "stage",
            )
        ).all()
        assert c.source_id == "FDA-LABEL-NDA217785"
        assert rows["Heterozygous Familial Hypercholesterolemia"].stage != Stage.approved


def test_manual_program_alias_merges_names(tmp_path):
    (tmp_path / "program_aliases.csv").write_text(
        "ticker,name,same_as,note\nRLAY,RLY-2608,Zovegalisib,10-K\n", encoding="utf-8"
    )
    pairs = ctgov._program_aliases(Inputs(manual_dir=tmp_path))
    assert pairs["RLAY"] == [("RLY-2608", "ZOVEGALISIB")]
    names = ctgov._Names()
    names.union(*pairs["RLAY"][0])
    names.uses["RLY-2608"] = names.uses["ZOVEGALISIB"] = 1
    assert names.find("RLY-2608") == names.find("ZOVEGALISIB")
