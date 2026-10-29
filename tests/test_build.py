import csv
import json
import shutil
from pathlib import Path

import httpx
import openpyxl
import pytest
from sqlmodel import Session, select

from intel.build import build_snapshot
from intel.cli import main
from intel.db import IntegrityViolation, provenance_gaps, rw_engine
from intel.enums import ClaimKind, Confidence, ExclusionCategory, PreferenceDimension
from intel.ingest import Inputs
from intel.ingest.mnc import WorkbookLayoutError
from intel.ingest.universe import STAGE0_COLUMNS
from intel.models import (
    DOMAIN_TABLES,
    Buyer,
    BuyerFinancial,
    BuyerPreference,
    BuyerProductLoe,
    Claim,
    MethodNote,
    Source,
    Target,
)

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = ROOT / "docs" / "assignment"
MNC = openpyxl.load_workbook(Inputs(assignment_dir=ASSIGNMENT).mnc_workbook, data_only=True)


def make_inputs(tmp: Path) -> Inputs:
    return Inputs(assignment_dir=ASSIGNMENT, raw_dir=tmp / "raw", manual_dir=tmp / "manual")


def build(tmp: Path, inputs: Inputs | None = None):
    db = tmp / "intel.db"
    report = build_snapshot(db, inputs or make_inputs(tmp))
    return db, report


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return build(tmp_path_factory.mktemp("build"))


@pytest.fixture
def s(built):
    with Session(rw_engine(built[0])) as session:
        yield session


def claims(s, entity, entity_id, field):
    return s.exec(
        select(Claim).where(
            Claim.entity_type == entity, Claim.entity_id == str(entity_id), Claim.field == field
        )
    ).all()


def sheet_rows(name):
    return [r for r in MNC[name].iter_rows(min_row=2, values_only=True) if r[0]]


# --- buyer workbook -------------------------------------------------------------------


def test_source_register_matches_sheet(s):
    rows = sheet_rows("来源登记")
    assert len(rows) == 43
    for sid, _, _, date_text, title, url, _ in rows:
        src = s.get(Source, sid)
        assert (src.url, src.title, src.published_date_text) == (url, title, str(date_text))
    mnc = s.exec(select(Source).where(Source.source_type == "mnc_material")).all()
    assert {x.source_id for x in mnc} == {r[0] for r in rows} | {"MNC-WB"}


def test_local_path_source_is_kept(s):
    local = [x for x in s.exec(select(Source)).all() if x.url and x.url.startswith("D:")]
    assert len(local) == 1


def test_buyers_match_summary_sheet(s):
    rows = sheet_rows("执行摘要")
    assert len(rows) == 10
    for row in rows:
        buyer = s.exec(select(Buyer).where(Buyer.ticker == row[1])).one()
        assert buyer.name_zh == row[0]
        assert buyer.financial_signals == row[2] and buyer.key_evidence == row[7]
        assert buyer.therapeutic_priorities == row[3] and buyer.buy_rationale == row[6]


def test_multi_source_cell_yields_claim_per_source(s):
    mrk = s.exec(select(Buyer).where(Buyer.ticker == "MRK")).one()
    found = claims(s, "buyer", mrk.id, "key_evidence")
    assert sorted(c.source_id for c in found) == ["MRK-1", "MRK-2", "MRK-3", "MRK-4", "MRK-5"]
    assert all(c.kind == ClaimKind.fact and c.value == mrk.key_evidence for c in found)
    assert "执行摘要!H2" in found[0].note


def test_inference_carries_sheet_confidence(s):
    pfe = s.exec(select(Buyer).where(Buyer.ticker == "PFE")).one()
    found = claims(s, "buyer", pfe.id, "therapeutic_priorities")
    assert found and all(
        c.kind == ClaimKind.inference and c.confidence == Confidence.medium_high for c in found
    )


def test_preferences_keep_sheet_order(s):
    assert len(s.exec(select(BuyerPreference)).all()) == 60
    mrk = s.exec(select(Buyer).where(Buyer.ticker == "MRK")).one()
    ta = sorted(
        (p for p in mrk.preferences if p.dimension == PreferenceDimension.therapeutic_area),
        key=lambda p: p.rank,
    )
    expected = [r[2] for r in sheet_rows("治疗领域分析") if r[0] == mrk.name_zh]
    assert [p.rank for p in ta] == [1, 2, 3] and [p.label for p in ta] == expected
    evidence = claims(s, "buyer_preference", ta[0].id, "evidence")
    profile = claims(s, "buyer_preference", ta[0].id, "target_profile")
    assert {c.kind for c in evidence} == {ClaimKind.fact}
    assert {c.kind for c in profile} == {ClaimKind.inference} and "继承" in profile[0].note


def test_overview_values_match_sheet(s):
    mrk = s.exec(select(Buyer).where(Buyer.ticker == "MRK")).one()
    fin = s.exec(select(BuyerFinancial).where(BuyerFinancial.buyer_id == mrk.id)).one()
    assert (fin.revenue_total, fin.currency, fin.fiscal_year) == (65.01, "USD", "FY2025")
    (c,) = claims(s, "buyer_financial", fin.id, "revenue_total")
    assert c.source_id == "MNC-WB" and c.kind == ClaimKind.fact and "原表数据来源" in c.note
    assert len(s.exec(select(BuyerProductLoe)).all()) == 38


def test_unverified_number_becomes_gap(s, built):
    jnj = s.exec(select(Buyer).where(Buyer.ticker == "JNJ")).one()
    tremfya = s.exec(
        select(BuyerProductLoe).where(
            BuyerProductLoe.buyer_id == jnj.id, BuyerProductLoe.product.startswith("Tremfya")
        )
    ).one()
    assert tremfya.revenue_us is None and tremfya.revenue_global == 5
    gaps = list(csv.DictReader(built[0].with_name("gaps.csv").open()))
    assert any(
        g["reason"] == "unverified_in_material" and g["location"].startswith("MNC买方概览!D")
        for g in gaps
    )


def test_partially_unverified_text_keeps_caveat(s, built):
    bmy = s.exec(select(Buyer).where(Buyer.ticker == "BMY")).one()
    fin = s.exec(select(BuyerFinancial).where(BuyerFinancial.buyer_id == bmy.id)).one()
    assert fin.recent_deals == "近年无大型并购[待核实]"
    (c,) = claims(s, "buyer_financial", fin.id, "recent_deals")
    assert "待核实" in c.note
    gaps = list(csv.DictReader(built[0].with_name("gaps.csv").open()))
    assert any(
        g["reason"] == "partially_unverified_in_material" and g["key"] == "BMY" for g in gaps
    )


def test_method_notes_available(s):
    items = {n.item: n.text for n in s.exec(select(MethodNote)).all()}
    assert "事实与推断" in items and "推断" in items["事实与推断"]


def test_unknown_company_alias_fails(tmp_path):
    assignment = tmp_path / "assignment"
    shutil.copytree(ASSIGNMENT, assignment)
    inputs = Inputs(assignment_dir=assignment, raw_dir=tmp_path / "raw")
    wb = openpyxl.load_workbook(inputs.mnc_workbook)
    wb["MNC买方概览"]["A19"] = "Mystery Pharma"
    wb.save(inputs.mnc_workbook)
    with pytest.raises(WorkbookLayoutError, match="Mystery Pharma"):
        build_snapshot(tmp_path / "x.db", inputs)


# --- universe -------------------------------------------------------------------------


def test_every_index_row_becomes_target(s):
    idx = openpyxl.load_workbook(Inputs(assignment_dir=ASSIGNMENT).index_workbook).worksheets[0]
    expected = {r[0] for r in idx.iter_rows(min_row=2, values_only=True) if r[0]}
    assert set(s.exec(select(Target.ticker)).all()) == expected and len(expected) == 149


def test_missing_sec_cache_is_a_gap_not_a_failure(s, built):
    assert all(t.cik is None for t in s.exec(select(Target)).all())
    assert built[1].gap_summary()["sec_tickers_cache_missing"] == 149


def write_sec_cache(inputs: Inputs, entries: list[dict]) -> None:
    inputs.sec_tickers.parent.mkdir(parents=True, exist_ok=True)
    inputs.sec_tickers.write_text(json.dumps({str(i): e for i, e in enumerate(entries)}))


def test_cik_mapping(tmp_path):
    inputs = make_inputs(tmp_path)
    write_sec_cache(inputs, [{"cik_str": 1682852, "ticker": "MRNA", "title": "Moderna, Inc."}])
    db, report = build(tmp_path, inputs)
    with Session(rw_engine(db)) as s:
        mrna = s.exec(select(Target).where(Target.ticker == "MRNA")).one()
        assert mrna.cik == "0001682852"
        (c,) = claims(s, "target", mrna.id, "cik")
        assert c.source_id == "SEC-TICKERS" and c.produced_by == "api"
        assert s.exec(select(Target).where(Target.ticker == "APGE")).one().cik is None
    assert report.gap_summary()["ticker_not_in_sec_file"] == 148


def write_stage0(inputs: Inputs, rows: list[dict]) -> None:
    inputs.stage0_exclusions.parent.mkdir(parents=True, exist_ok=True)
    with inputs.stage0_exclusions.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=STAGE0_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in STAGE0_COLUMNS})


STAGE0_ROW = dict(
    ticker="APGE",
    category="acquired",
    reason="Acquired by AbbVie",
    kind="fact",
    source_id="PR-APGE-1",
    source_type="press_release",
    source_url="https://example.com/abbvie-apogee",
    source_title="AbbVie completes acquisition",
    published_date="2026-09",
    accessed_on="2026-10-29",
    verified_by="ZY",
)


def test_verified_exclusion_and_unverified_draft(tmp_path):
    inputs = make_inputs(tmp_path)
    draft = STAGE0_ROW | dict(
        ticker="TWST",
        category="non_therapeutic",
        kind="inference",
        confidence="high",
        source_id="SEC-TWST-10K",
        source_type="sec_filing",
        verified_by="",
    )
    write_stage0(inputs, [STAGE0_ROW, draft])
    db, report = build(tmp_path, inputs)
    with Session(rw_engine(db)) as s:
        apge = s.exec(select(Target).where(Target.ticker == "APGE")).one()
        assert apge.excluded and apge.exclusion_category == ExclusionCategory.acquired
        (c,) = claims(s, "target", apge.id, "exclusion_reason")
        assert c.kind == ClaimKind.fact and c.source_id == "PR-APGE-1"
        assert s.get(Source, "PR-APGE-1").published_date is None
        assert not s.exec(select(Target).where(Target.ticker == "TWST")).one().excluded
        pool = s.exec(select(Target).where(Target.excluded == False)).all()  # noqa: E712
        excluded = s.exec(select(Target).where(Target.excluded == True)).all()  # noqa: E712
        assert len(pool) + len(excluded) == 149 and len(excluded) == 1
        assert provenance_gaps(s) == []
    assert any("1 unverified Stage 0 row" in n and "TWST" in n for n in report.notes)


def test_inference_exclusion_needs_confidence(tmp_path):
    inputs = make_inputs(tmp_path)
    write_stage0(inputs, [STAGE0_ROW | dict(category="buyer_scale", kind="inference")])
    with pytest.raises(IntegrityViolation, match="confidence"):
        build(tmp_path, inputs)


# --- build mechanics ------------------------------------------------------------------


def dump(db: Path):
    with Session(rw_engine(db)) as s:
        out = {
            m.__tablename__: [r.model_dump() for r in s.exec(select(m)).all()]
            for m in (*DOMAIN_TABLES, Source, Claim, MethodNote)
        }
    return json.loads(json.dumps(out, default=str))


def test_rebuild_is_repeatable(tmp_path, built):
    db, _ = build(tmp_path)
    assert dump(db) == dump(built[0])


def test_build_works_offline(tmp_path, monkeypatch, built):
    def no_network(*_a, **_k):
        raise AssertionError("build must not use the network")

    monkeypatch.setattr(httpx.Client, "send", no_network)
    db, _ = build(tmp_path)
    assert dump(db) == dump(built[0])


def bad_step(ctx):
    ctx.claim("target", 1, "cik", "x", "NOT-REGISTERED")


def test_failed_build_keeps_old_snapshot(tmp_path):
    db, _ = build(tmp_path)
    before = db.read_bytes()
    with pytest.raises(IntegrityViolation):
        build_snapshot(db, make_inputs(tmp_path), steps=[bad_step])
    assert db.read_bytes() == before
    assert not db.with_name(db.name + ".tmp").exists()


def test_cli_build_failure_exits_nonzero(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("intel.build.default_steps", lambda: [bad_step])
    assert main(["build", "--db", str(tmp_path / "x.db")]) == 1
    assert "snapshot unchanged" in capsys.readouterr().err


def test_gap_report_written(built):
    rows = list(csv.DictReader(built[0].with_name("gaps.csv").open()))
    assert rows and set(rows[0]) == {"entity", "key", "field", "reason", "location"}
    assert len(rows) == len(built[1].gaps)
