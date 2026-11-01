import hashlib
import json
from datetime import UTC, date, datetime

import httpx
import pytest
from sqlmodel import Session, select

from intel.db import init_db, provenance_gaps
from intel.docs.documents import COLUMNS
from intel.enums import ClaimKind, ProducedBy, SourceType
from intel.extract import review
from intel.extract.load import ExtractionLoadError, ingest, parse_window
from intel.ingest import BuildContext, Inputs
from intel.models import Catalyst, Claim, Program, Source, Target, Trial, TrialResult

TEXT = (
    "VK2735 is a dual agonist of the GLP-1 and GIP receptors.\n"
    "The VENTURE study met its primary endpoint, with mean weight loss of up to 14.7% at week 13 "
    "versus 1.7% for placebo.\n"
    "Viking expects to initiate a Phase 3 program in the second half of 2027.\n"
    "A regulatory submission is planned around the time of the next financing.\n"
)
SID = "DOC-VKTX-0001"


@pytest.mark.parametrize(
    ("timing", "window"),
    [
        ("Q1 2027", ("2027-01-01", "2027-03-31")),
        ("4Q 2026", ("2026-10-01", "2026-12-31")),
        ("the third quarter of 2027", ("2027-07-01", "2027-09-30")),
        ("second half of 2027", ("2027-07-01", "2027-12-31")),
        ("2H 2027", ("2027-07-01", "2027-12-31")),
        ("1H27 2027", None),  # 1H27 is not a clean token
        ("mid-2027", ("2027-06-01", "2027-08-31")),
        ("by year-end 2026", ("2026-10-01", "2026-12-31")),
        ("2027", ("2027-01-01", "2027-12-31")),
        ("in 2028", ("2028-01-01", "2028-12-31")),
        ("late 2026 or early 2027", None),
        ("early 2027", None),
        ("around the next financing", None),
    ],
)
def test_parse_window(timing, window):
    got = parse_window(timing)
    assert (tuple(d.isoformat() for d in got) if got else None) == window


def make_inputs(tmp_path, items, signed="zyx"):
    manual, raw = tmp_path / "manual", tmp_path / "raw"
    (manual / "extractions").mkdir(parents=True)
    docs_dir = raw / "docs" / "VKTX"
    docs_dir.mkdir(parents=True)
    (docs_dir / f"{SID}.txt").write_text(TEXT)
    meta = {"status": "ok", "fetched_at": "2026-10-30T10:00:00+00:00",
            "text_sha256": hashlib.sha256(TEXT.encode()).hexdigest()}  # fmt: skip
    (docs_dir / f"{SID}.meta.json").write_text(json.dumps(meta))
    (manual / "documents.csv").write_text(
        ",".join(COLUMNS) + f"\nVKTX,https://www.sec.gov/x.htm,press_release,PR,2026-08-01,{SID},\n"
    )
    rev = review.ExtractionReview("VKTX", signed, items)
    (manual / "extractions" / "VKTX.toml").write_text(review.dumps(rev))
    return Inputs(manual_dir=manual, raw_dir=raw)


def item(kind, values, quotes, decision="accept", iid=None):
    return review.ReviewItem(
        id=iid or f"{kind[0]}-{len(quotes[0])}", type=kind, source_id=SID, values=values,
        quotes=quotes, model="deepseek-v4-pro", returned_model="deepseek-v4-pro-1017",
        check="agreed", decision=decision,
    )  # fmt: skip


MOA = "dual agonist of the GLP-1 and GIP receptors"
PROGRAM = item(
    "program", {"asset": "vk-2735", "mechanism": MOA, "modality": ""}, [f"VK2735 is a {MOA}"]
)
RESULT = item(
    "clinical_result",
    {"asset": "VK2735", "trial": "NCT05000000", "indication": "obesity",
     "endpoint": "mean weight loss at week 13", "result": "up to 14.7% vs 1.7%", "analysis": "",
     "comparator": "placebo", "advantage_vs_soc": "", "confidence": ""},
    ["met its primary endpoint, with mean weight loss of up to 14.7% at week 13 versus 1.7%"],
)  # fmt: skip
CATALYST = item(
    "catalyst",
    {"asset": "VK2735", "event": "initiate a Phase 3 program", "event_type": "trial_start",
     "timing": "second half of 2027"},
    ["expects to initiate a Phase 3 program in the second half of 2027"],
)  # fmt: skip


@pytest.fixture
def world(session):
    target = Target(ticker="VKTX", name="Viking")
    session.add(target)
    session.flush()
    session.add(Program(target_id=target.id, name="VK2735"))
    session.add(Trial(nct_id="NCT05000000", target_id=target.id))
    session.flush()
    return session


def run(world, inputs):
    ctx = BuildContext(session=world, inputs=inputs)
    ingest(ctx)
    world.flush()
    return ctx


def test_accepted_items_written_with_llm_claims(world, tmp_path):
    ctx = run(world, make_inputs(tmp_path, [PROGRAM, RESULT, CATALYST]))
    program = world.exec(select(Program)).one()
    assert program.mechanism == "dual agonist of the GLP-1 and GIP receptors"
    result = world.exec(select(TrialResult)).one()
    assert (result.result, result.comparator) == ("up to 14.7% vs 1.7%", "placebo")
    cat = world.exec(select(Catalyst)).one()
    assert (cat.window_start, cat.window_end) == (date(2027, 7, 1), date(2027, 12, 31))
    assert cat.program_id == program.id and "second half of 2027" in cat.event
    claims = world.exec(select(Claim)).all()
    assert claims and all(c.produced_by == ProducedBy.llm and c.quote for c in claims)
    assert {c.model for c in claims} == {"deepseek-v4-pro-1017"}
    assert {c.as_of for c in claims} == {date(2026, 8, 1)}
    source = world.get(Source, SID)
    assert source.source_type == SourceType.press_release and len(source.content_hash) == 64
    assert provenance_gaps(world) == []
    assert ctx.notes == ["extractions: 3 accepted item(s) loaded, 0 not reviewed"]


def test_unsigned_file_ignored(world, tmp_path):
    ctx = run(world, make_inputs(tmp_path, [PROGRAM], signed=""))
    assert world.exec(select(Program)).one().mechanism is None and ctx.notes == []


def test_undecided_and_rejected_items_skipped(world, tmp_path):
    undecided = item("catalyst", CATALYST.values, CATALYST.quotes, decision="", iid="e-1")
    rejected = item("catalyst", CATALYST.values, CATALYST.quotes, decision="reject", iid="e-2")
    ctx = run(world, make_inputs(tmp_path, [undecided, rejected]))
    assert world.exec(select(Catalyst)).all() == []
    assert ctx.notes == ["extractions: 0 accepted item(s) loaded, 1 not reviewed"]


def test_edited_quote_fails(world, tmp_path):
    bad = item("program", PROGRAM.values, ["VK2735 is a triple agonist of three receptors"])
    with pytest.raises(ExtractionLoadError, match="quote_not_in_text"):
        run(world, make_inputs(tmp_path, [bad]))


def test_tampered_archive_fails(world, tmp_path):
    inputs = make_inputs(tmp_path, [PROGRAM])
    path = inputs.docs_dir / "VKTX" / f"{SID}.txt"
    path.write_text(TEXT + "extra")
    with pytest.raises(ExtractionLoadError, match="hash differs"):
        run(world, inputs)


def test_missing_archive_fails(world, tmp_path):
    inputs = make_inputs(tmp_path, [PROGRAM])
    (inputs.docs_dir / "VKTX" / f"{SID}.txt").unlink()
    with pytest.raises(ExtractionLoadError, match=SID):
        run(world, inputs)


def test_unmatched_asset_and_trial_become_gaps(world, tmp_path):
    other = item("program", PROGRAM.values | {"asset": "VK9999"}, PROGRAM.quotes, iid="p-x")
    no_nct = item("clinical_result", RESULT.values | {"trial": "VENTURE"}, RESULT.quotes)
    ctx = run(world, make_inputs(tmp_path, [other, no_nct]))
    assert sorted((g.entity, g.reason) for g in ctx.gaps) == [
        ("program", "extraction_unmatched"), ("trial_result", "extraction_unmatched")]  # fmt: skip


def test_unparsed_timing_keeps_text_and_records_gap(world, tmp_path):
    vague = item(
        "catalyst",
        {"asset": "", "event": "regulatory submission", "event_type": "regulatory_filing",
         "timing": "around the time of the next financing"},
        ["A regulatory submission is planned around the time of the next financing"],
    )  # fmt: skip
    ctx = run(world, make_inputs(tmp_path, [vague]))
    cat = world.exec(select(Catalyst)).one()
    assert cat.window_start is None and "next financing" in cat.event
    assert [g.reason for g in ctx.gaps] == ["timing_not_parsed"]


def test_advantage_is_inference_with_confidence(world, tmp_path):
    adv = item(
        "clinical_result",
        RESULT.values | {"advantage_vs_soc": "greater weight loss than placebo",
                         "confidence": "medium"},
        RESULT.quotes,
    )  # fmt: skip
    run(world, make_inputs(tmp_path, [adv]))
    claim = world.exec(select(Claim).where(Claim.field == "advantage_vs_soc")).one()
    assert claim.kind == ClaimKind.inference and claim.confidence.value == "medium"


def test_build_needs_no_model_keys(tmp_path, monkeypatch):
    for key in ("LLM_API_KEY", "LLM_VERIFY_API_KEY", "LLM_BASE_URL"):
        monkeypatch.delenv(key, raising=False)

    def no_network(*a, **k):
        raise AssertionError("build must not call the network")

    monkeypatch.setattr(httpx.Client, "send", no_network)
    engine = init_db(tmp_path / "s.db")
    with Session(engine) as s:
        t = Target(ticker="VKTX", name="Viking")
        s.add(t)
        s.flush()
        s.add(Program(target_id=t.id, name="VK2735"))
        s.flush()
        ctx = run(s, make_inputs(tmp_path, [PROGRAM]))
    assert ctx.notes[0].startswith("extractions: 1 accepted")


def test_hand_edited_controlled_values_fail_with_location(world, tmp_path):
    bad_type = item("catalyst", CATALYST.values | {"event_type": "launch"}, CATALYST.quotes)
    with pytest.raises(ExtractionLoadError, match=r"VKTX.toml item c-64: event_type"):
        run(world, make_inputs(tmp_path / "a", [bad_type]))
    no_conf = item("clinical_result", RESULT.values | {"advantage_vs_soc": "better"}, RESULT.quotes)
    with pytest.raises(ExtractionLoadError, match="needs confidence"):
        run(world, make_inputs(tmp_path / "b", [no_conf]))


def test_existing_manual_source_gets_archive_fields(world, tmp_path):
    inputs = make_inputs(tmp_path, [PROGRAM])
    text = (inputs.manual_dir / "documents.csv").read_text().replace(SID, "MAN-VKTX-9")
    (inputs.manual_dir / "documents.csv").write_text(text)
    for suffix in (".txt", ".meta.json"):
        (inputs.docs_dir / "VKTX" / f"{SID}{suffix}").rename(
            inputs.docs_dir / "VKTX" / f"MAN-VKTX-9{suffix}"
        )
    ext = inputs.extractions_dir / "VKTX.toml"
    ext.write_text(ext.read_text().replace(SID, "MAN-VKTX-9"))
    world.add(Source(source_id="MAN-VKTX-9", source_type=SourceType.press_release,
                     fetched_at=datetime(2026, 10, 30, tzinfo=UTC)))  # fmt: skip
    world.flush()
    run(world, inputs)
    sources = world.exec(select(Source).where(Source.source_id == "MAN-VKTX-9")).all()
    assert len(sources) == 1 and sources[0].local_path.endswith("MAN-VKTX-9.txt")
    assert len(sources[0].content_hash) == 64


# --- trial name matching ---------------------------------------------------------------


def study(nct, title, acronym=None, org_id=None):
    ident = {"nctId": nct, "briefTitle": title} | ({"acronym": acronym} if acronym else {})
    if org_id:
        ident["orgStudyIdInfo"] = {"id": org_id}
    return {"protocolSection": {"identificationModule": ident}}


@pytest.fixture
def shasta(session):
    target = Target(ticker="VKTX", name="Viking")
    session.add(target)
    session.flush()
    session.add(Program(target_id=target.id, name="VK2735"))
    for nct in ("NCT06347003", "NCT06347016", "NCT07104383", "NCT05693142", "NCT00000002"):
        session.add(Trial(nct_id=nct, target_id=target.id))
    session.flush()
    return session


def with_registry(inputs):
    path = inputs.raw_dir / "ctgov" / "VKTX.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    studies = [
        study("NCT06347003", "Study of Plozasiran in Adults With sHTG", "SHASTA-3"),
        study("NCT06347016", "Study of Plozasiran in Adults With sHTG", "SHASTA-4"),
        study("NCT07104383", "VK2735 for Weight Management Phase 3 (VANQUISH 2)"),
        study("NCT05693142", "AFFINITY DUCHENNE: RGX-202 Gene Therapy in DMD"),
        study("NCT00000002", "A Phase 1 Study of VK2735 in Obese Adults", org_id="VK2735-103"),
        study("NCT09999999", "Another trial (VANQUISH 2)"),  # not in the snapshot
    ]
    path.write_text(json.dumps({"studies": studies}))
    return inputs


def result_with_trial(trial, iid):
    return item("clinical_result", RESULT.values | {"trial": trial}, RESULT.quotes, iid=iid)


@pytest.mark.parametrize(
    ("trial", "nct", "basis"),
    [
        ("SHASTA-3 study", "NCT06347003", "CT.gov 登记名称对照：「SHASTA-3」"),
        ("the Phase 3 VANQUISH-2 trial", "NCT07104383", "「VANQUISH 2」"),
        ("Affinity Duchenne", "NCT05693142", "「AFFINITY DUCHENNE」"),
        ("VK2735-103 Maintenance Study", "NCT00000002", "「VK2735-103」"),
    ],
)
def test_trial_matched_by_registry_name(shasta, tmp_path, trial, nct, basis):
    inputs = with_registry(make_inputs(tmp_path, [result_with_trial(trial, "r-1")]))
    run(shasta, inputs)
    row = shasta.exec(select(TrialResult)).one()
    assert shasta.get(Trial, row.trial_id).nct_id == nct
    claim = shasta.exec(select(Claim).where(Claim.field == "result")).one()
    assert basis in claim.note


def test_ambiguous_trial_name_is_a_gap(shasta, tmp_path):
    inputs = with_registry(make_inputs(tmp_path, [result_with_trial("SHASTA-3 and SHASTA-4", "r")]))
    ctx = run(shasta, inputs)
    assert shasta.exec(select(TrialResult)).all() == []
    assert [g.reason for g in ctx.gaps] == ["extraction_trial_ambiguous"]


def write_aliases(inputs, rows):
    lines = [",".join(("ticker", "name", "nct_id", "source_id", "note", "verified_by"))]
    lines += [",".join(r) for r in rows]
    inputs.trial_aliases.write_text("\n".join(lines) + "\n")


def test_trial_matched_by_signed_manual_alias(shasta, tmp_path):
    inputs = with_registry(
        make_inputs(tmp_path, [result_with_trial("VK2735-102 Maintenance", "r")])
    )
    write_aliases(inputs, [("VKTX", "VK2735-102", "NCT00000002", SID, "", "zyx")])
    run(shasta, inputs)
    row = shasta.exec(select(TrialResult)).one()
    assert shasta.get(Trial, row.trial_id).nct_id == "NCT00000002"
    claim = shasta.exec(select(Claim).where(Claim.field == "result")).one()
    assert "人工对照表" in claim.note and SID in claim.note


def test_unsigned_manual_alias_ignored(shasta, tmp_path):
    inputs = with_registry(
        make_inputs(tmp_path, [result_with_trial("VK2735-102 Maintenance", "r")])
    )
    write_aliases(inputs, [("VKTX", "VK2735-102", "NCT00000002", SID, "", "")])
    ctx = run(shasta, inputs)
    assert [g.reason for g in ctx.gaps] == ["extraction_unmatched"]


def test_manual_alias_with_unregistered_source_fails(shasta, tmp_path):
    from intel.extract.trials import TrialAliasError

    inputs = with_registry(make_inputs(tmp_path, [result_with_trial("VK2735-102", "r")]))
    write_aliases(inputs, [("VKTX", "VK2735-102", "NCT00000002", "MAN-NOPE-1", "", "zyx")])
    with pytest.raises(TrialAliasError, match="MAN-NOPE-1"):
        run(shasta, inputs)


def test_registry_names_and_program_names_excluded():
    from intel.extract.trials import _usable, registry_names, tokens

    s = study("NCT1", "AFFINITY DUCHENNE: Gene Therapy in Boys (DMD) (Phase 3) (VANQUISH 2)", "AFF")
    assert registry_names(s) == ["AFF", "Phase 3", "VANQUISH 2", "AFFINITY DUCHENNE"]
    assert not _usable(tokens("Phase 3"))  # generic words name no particular trial
    assert _usable(tokens("VANQUISH 2")) and _usable(tokens("SHASTA-3"))


def test_most_specific_name_wins_and_acronym_led_names(session, tmp_path):
    from intel.extract.trials import TrialMatcher

    target = Target(ticker="ARWR", name="Arrowhead")
    session.add(target)
    session.flush()
    for nct in ("NCT1", "NCT2", "NCT3", "NCT4"):
        session.add(Trial(nct_id=nct, target_id=target.id))
    session.flush()
    studies = [
        study("NCT1", "Study of Plozasiran in Mixed Dyslipidemia", "MUIR"),
        study("NCT2", "Phase 3 Study of Plozasiran", "MUIR-3"),
        study("NCT3", "VK2735 for Weight Management Phase 2", "VENTURE"),
        study("NCT4", "VK2735 Phase 2 (Venture Oral Dosing)"),
    ]
    d = tmp_path
    (d / "ARWR.json").write_text(json.dumps({"studies": studies}))
    m = TrialMatcher(session, d, {})
    assert m.match(target, "MUIR-3 trial").trial.nct_id == "NCT2"
    assert m.match(target, "MUIR").trial.nct_id == "NCT1"
    assert m.match(target, "VENTURE-Oral Dosing study").trial.nct_id == "NCT4"
    assert m.match(target, "VENTURE").trial.nct_id == "NCT3"


def test_registry_names_include_sponsor_study_id():
    from intel.extract.trials import registry_names

    assert registry_names(study("NCT1", "A Study", org_id="VK2735-102")) == ["VK2735-102"]
    assert registry_names(study("NCT1", "A Study", org_id="PROTOCOL")) == []  # no digit


@pytest.mark.parametrize(
    ("asset", "names", "expected"),
    [
        ("clemidsogene lanparvovec (RGX-121)", ["RGX-121-3102", "RGX-121"], "RGX-121"),
        (
            "defactinib",
            ["AVUTOMETINIB AND DEFACTINIB", "DEFACTINIB (PART A - VS-6063, VS-6063)"],
            "DEFACTINIB (PART A - VS-6063, VS-6063)",
        ),
        ("ABBV-RGX-314 (sura-vec)", ["RGX-314", "RGX-121"], "RGX-314"),
        (
            "avutometinib plus defactinib",
            ["AVUTOMETINIB DEFACTINIB", "AVUTOMETINIB"],
            "AVUTOMETINIB DEFACTINIB",
        ),
        ("VK2735", ["VK2735 (A)", "VK2735 (B)"], None),  # two programs, neither more exact
        ("ARO-DUX4", ["ARO-DUX", "ARO-HBV"], None),
    ],
)
def test_match_program_by_name_brackets_and_containment(asset, names, expected):
    from intel.extract.load import match_program

    programs = [Program(name=n) for n in names]
    found = match_program(programs, asset)
    assert (found.name if found else None) == expected


def test_none_comparator_is_left_empty(world, tmp_path):
    single_arm = item("clinical_result", RESULT.values | {"comparator": "none"}, RESULT.quotes)
    run(world, make_inputs(tmp_path, [single_arm]))
    assert world.exec(select(TrialResult)).one().comparator is None
    assert not world.exec(select(Claim).where(Claim.field == "comparator")).all()
