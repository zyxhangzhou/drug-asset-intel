import csv
import shutil
from pathlib import Path

import pytest
from sqlmodel import Session, select
from test_ctgov import SYNTHETIC, raw_with
from test_financials import PRICE_ROWS, SHARES, duration, facts, instant, write_company

from intel.build import build_snapshot
from intel.db import provenance_gaps, rw_engine
from intel.enums import ClaimKind, ResearchStatus
from intel.ingest import Inputs
from intel.ingest import financials as fin
from intel.models import Claim, Match, Recommendation, Target
from intel.scoring import screen
from intel.scoring.review import ReviewError

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "data" / "manual"

REVIEW = """
verified_by = "tester"
program = "VK2735"
indication = "Obesity"
buyer = "Novo Nordisk"
preference_rank = 1
deal_form = "收购"
need_item = "更高减重的下一代 GLP-1 组合"
match_note = "VK2735 是 GLP-1/GIP 双激动剂"
thesis = ["诺和诺德需要下一代减重药；VK2735 对应。", "证据是 2 期结果；下一事件是 3 期读出。"]
thesis_sources = ["MAN-VKTX-1"]

[scores.buyer_fit]
score = 4
reason = "对应目标资产画像"
sources = ["MAN-VKTX-1"]

[event]
text = "VANQUISH 3 期读出"
timing = "2027H1"
importance = "high"
certainty = "disclosed"
sources = ["MAN-VKTX-1"]

[rights]
status = "{rights}"
note = "10-K 未披露对外授权"
sources = ["MAN-VKTX-1"]
"""

SOURCES = (
    "source_id,url,source_type,title,publisher,published_date,accessed_on,note\n"
    "MAN-VKTX-1,https://ir.vikingtherapeutics.com/x,press_release,PR,Viking,2026-07-23,2026-10-30,\n"
)


def manual_dir(tmp: Path, review: str | None = None, sources: str = SOURCES) -> Path:
    m = tmp / "manual"
    m.mkdir()
    shutil.copy(MANUAL / "ta_keywords.csv", m)
    with (MANUAL / "buyer_preference_map.csv").open(encoding="utf-8") as src:
        rows = list(csv.DictReader(src))
    with (m / "buyer_preference_map.csv").open("w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow(r | {"verified_by": "tester"})
    (m / "sources.csv").write_text(sources, encoding="utf-8")
    if review is not None:
        (m / "reviews").mkdir()
        (m / "reviews" / "VKTX.toml").write_text(review, encoding="utf-8")
    return m


def build(tmp: Path, manual: Path):
    raw = raw_with(tmp, {"VKTX": SYNTHETIC})
    burning = facts(
        {fin.CASH: [instant(500_000_000.0)], fin.OCF: [duration(-120_000_000.0)]}, shares=SHARES
    )
    write_company(raw, "VKTX", "1607678", burning, PRICE_ROWS)
    inputs = Inputs(assignment_dir=ROOT / "docs" / "assignment", raw_dir=raw, manual_dir=manual)
    db = tmp / "intel.db"
    report = build_snapshot(db, inputs)
    return db, report


def primary(s, ticker) -> Recommendation:
    t = s.exec(select(Target).where(Target.ticker == ticker)).one()
    return s.exec(
        select(Recommendation).where(Recommendation.target_id == t.id, Recommendation.is_primary)
    ).one()


@pytest.fixture(scope="module")
def auto(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("auto")
    db, _ = build(tmp, manual_dir(tmp))
    with Session(rw_engine(db)) as s:
        yield s, tmp


def test_auto_pair_scores(auto):
    s, _ = auto
    rec = primary(s, "VKTX")
    assert rec.indication.indication == "Obesity"
    assert (rec.buyer_fit, rec.stage_match, rec.catalyst) == (2, 4, 3)
    assert rec.clinical is None  # synthetic trials have no posted results
    assert rec.dealability == 4  # EV = 1.8B − 0.5B
    assert rec.research_status == ResearchStatus.auto and rec.rights_status is None
    assert rec.optimistic > rec.conservative
    (c,) = s.exec(
        select(Claim).where(
            Claim.entity_type == "recommendation",
            Claim.entity_id == str(rec.id),
            Claim.field == "event_timing",
        )
    ).all()
    assert c.kind == ClaimKind.fact and c.source_id.startswith("CTG-")


def test_matrix_has_row_per_buyer(auto):
    s, _ = auto
    t = s.exec(select(Target).where(Target.ticker == "VKTX")).one()
    buyers = {m.buyer.name for m in s.exec(select(Match).where(Match.target_id == t.id))}
    assert {"Novo Nordisk", "Pfizer"} <= buyers


def test_outputs_and_provenance(auto):
    s, tmp = auto
    assert provenance_gaps(s) == []
    longlist = list(csv.DictReader((tmp / "longlist.csv").open(encoding="utf-8")))
    opt = [float(r["optimistic"]) for r in longlist]
    assert opt == sorted(opt, reverse=True)
    no_asset = [r for r in longlist if not r["asset"]]
    assert all(r["in_longlist"] == "False" for r in no_asset)
    shortlist = (tmp / "shortlist.csv").read_text(encoding="utf-8").strip().splitlines()
    assert len(shortlist) == 1  # header only without reviews


def test_unverified_map_means_no_buyer(tmp_path):
    m = manual_dir(tmp_path)
    rows = list(csv.DictReader((MANUAL / "buyer_preference_map.csv").open(encoding="utf-8")))
    with (m / "buyer_preference_map.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({**r, "verified_by": ""} for r in rows)
    db, _ = build(tmp_path, m)
    with Session(rw_engine(db)) as s:
        rec = primary(s, "VKTX")
        assert rec.buyer_preference_id is None and rec.buyer_fit == 0


def test_review_shortlists_with_verified_rights(tmp_path):
    db, _ = build(tmp_path, manual_dir(tmp_path, REVIEW.replace("{rights}", "full")))
    with Session(rw_engine(db)) as s:
        rec = primary(s, "VKTX")
        assert rec.research_status == ResearchStatus.reviewed
        assert (rec.buyer_fit, rec.catalyst) == (4, 4)
        assert rec.preference.buyer.name == "Novo Nordisk"
        target = s.exec(select(Target).where(Target.ticker == "VKTX")).one()
        assert target.shortlisted and target.selection_rationale.startswith("诺和诺德")
        assert provenance_gaps(s) == []


def test_unsigned_review_is_ignored(tmp_path):
    review = REVIEW.replace('verified_by = "tester"', 'verified_by = ""')
    db, _ = build(tmp_path, manual_dir(tmp_path, review.replace("{rights}", "full")))
    with Session(rw_engine(db)) as s:
        assert primary(s, "VKTX").research_status == ResearchStatus.auto


def test_unknown_source_fails_build(tmp_path):
    review = REVIEW.replace("{rights}", "full").replace(
        '["MAN-VKTX-1"]\n\n[event]', '["MAN-NOPE"]\n\n[event]'
    )
    with pytest.raises(ReviewError, match="MAN-NOPE"):
        build(tmp_path, manual_dir(tmp_path, review))


def test_restricted_rights_block_acquisition(tmp_path):
    db, _ = build(tmp_path, manual_dir(tmp_path, REVIEW.replace("{rights}", "restricted")))
    with Session(rw_engine(db)) as s:
        assert not s.exec(select(Target).where(Target.ticker == "VKTX")).one().shortlisted
    row = next(
        r
        for r in csv.DictReader((tmp_path / "longlist.csv").open(encoding="utf-8"))
        if r["ticker"] == "VKTX"
    )
    assert row["not_shortlisted_reason"] == "资产权益受限，与收购方案不兼容"


@pytest.mark.parametrize(
    ("text", "sig"),
    [
        ("p <.0001, Vaccine Efficacy", True),
        ("p = 0.049", True),
        ("p=0.05", False),
        ("GMR 1.07", False),
    ],
)
def test_p_value_parse(text, sig):
    assert screen.significant(text) is sig


def test_shortlist_api_reweights(auto, tmp_path):
    from fastapi.testclient import TestClient

    from intel.api import create_app

    _, tmp = auto
    client = TestClient(create_app(db_path=tmp / "intel.db", web_dist=tmp_path))
    default = client.get("/api/shortlist").json()
    vktx = next(i for i in default["items"] if i["ticker"] == "VKTX")
    with Session(rw_engine(tmp / "intel.db")) as s:
        assert vktx["conservative"] == primary(s, "VKTX").conservative
    no_fit = client.get("/api/shortlist", params={"weights": "0,20,20,15,15"}).json()
    assert no_fit["weights"]["buyer_fit"] == 0
    vktx2 = next(i for i in no_fit["items"] if i["ticker"] == "VKTX")
    assert vktx2["conservative"] != vktx["conservative"]
    assert client.get("/api/shortlist", params={"weights": "1,2"}).status_code == 422


def test_unsupported_high_score_is_reported(tmp_path):
    from intel.cli import main

    db, _ = build(tmp_path, manual_dir(tmp_path))
    assert main(["check-scoring", "--db", str(db)]) == 0
    with Session(rw_engine(db)) as s:
        rec = primary(s, "VKTX")
        rec.buyer_fit = 4  # no need_item behind it
        s.add(rec)
        s.commit()
    assert main(["check-scoring", "--db", str(db)]) == 1


def test_no_registered_event_in_window_scores_zero(tmp_path):
    late = [
        {
            **SYNTHETIC[0],
            "protocolSection": {
                **SYNTHETIC[0]["protocolSection"],
                "statusModule": {
                    **SYNTHETIC[0]["protocolSection"]["statusModule"],
                    "primaryCompletionDateStruct": {"date": "2030-01", "type": "ESTIMATED"},
                },
            },
        }
    ]
    raw = raw_with(tmp_path, {"VKTX": late})
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment", raw_dir=raw, manual_dir=manual_dir(tmp_path)
    )
    build_snapshot(tmp_path / "x.db", inputs)
    with Session(rw_engine(tmp_path / "x.db")) as s:
        rec = primary(s, "VKTX")
        assert rec.catalyst == 0 and rec.next_event is None


def test_longlist_extra_pulls_company_in(tmp_path):
    cfg = (ROOT / "config" / "scoring.toml").read_text(encoding="utf-8")
    cfg = cfg.replace("longlist_size = 40", "longlist_size = 0")
    cfg = cfg.replace('longlist_extra = ["IONS", "VNDA"]', 'longlist_extra = ["VKTX"]')
    (tmp_path / "scoring.toml").write_text(cfg, encoding="utf-8")
    raw = raw_with(tmp_path, {"VKTX": SYNTHETIC})
    write_company(raw, "VKTX", "1607678", facts({}, shares=SHARES), PRICE_ROWS)
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment",
        raw_dir=raw,
        manual_dir=manual_dir(tmp_path),
        scoring_config=tmp_path / "scoring.toml",
    )
    build_snapshot(tmp_path / "intel.db", inputs)
    rows = csv.DictReader((tmp_path / "longlist.csv").open(encoding="utf-8"))
    assert {r["ticker"] for r in rows if r["in_longlist"] == "True"} == {"VKTX"}


def test_reviewed_company_stays_in_review_pool(tmp_path):
    cfg = (ROOT / "config" / "scoring.toml").read_text(encoding="utf-8")
    (tmp_path / "scoring.toml").write_text(
        cfg.replace("longlist_size = 40", "longlist_size = 0"), encoding="utf-8"
    )
    raw = raw_with(tmp_path, {"VKTX": SYNTHETIC})
    write_company(raw, "VKTX", "1607678", facts({}, shares=SHARES), PRICE_ROWS)
    inputs = Inputs(
        assignment_dir=ROOT / "docs" / "assignment",
        raw_dir=raw,
        manual_dir=manual_dir(tmp_path, REVIEW.replace("{rights}", "full")),
        scoring_config=tmp_path / "scoring.toml",
    )
    build_snapshot(tmp_path / "intel.db", inputs)
    rows = csv.DictReader((tmp_path / "longlist.csv").open(encoding="utf-8"))
    assert {r["ticker"] for r in rows if r["in_longlist"] == "True"} == {"VKTX"}
