from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from intel import views
from intel.api import create_app
from intel.db import rw_engine
from intel.enums import ClaimKind, Confidence, ProducedBy, SourceType, Stage
from intel.models import (
    Buyer,
    BuyerPreference,
    Claim,
    Match,
    Program,
    ProgramIndication,
    Source,
    Target,
    Trial,
    TrialResult,
)

SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "processed" / "intel.db"


def claim(entity, field, source_id, value, **kw) -> Claim:
    kw.setdefault("kind", ClaimKind.fact)
    kw.setdefault("produced_by", ProducedBy.api)
    return Claim(
        entity_type=entity.__tablename__,
        entity_id=str(entity.id),
        field=field,
        value=value,
        source_id=source_id,
        **kw,
    )


@pytest.fixture
def raw_dir(tmp_path):
    path = tmp_path / "raw"
    (path / "docs" / "ABCD").mkdir(parents=True)
    (path / "docs" / "ABCD" / "DOC-ABCD-1.txt").write_text("ABC-101 is a GLP-1 agonist.", "utf-8")
    (path / "ctgov.json").write_text("{}", "utf-8")
    (tmp_path / "secret.txt").write_text("outside", "utf-8")
    return path


@pytest.fixture
def seeded(db_path, raw_dir):
    now = datetime.now(UTC)
    with Session(rw_engine(db_path)) as s:
        s.add_all(
            [
                Source(
                    source_id="CTG-NCT00000001",
                    source_type=SourceType.ctgov,
                    url="https://clinicaltrials.gov/study/NCT00000001",
                    fetched_at=now,
                ),
                Source(
                    source_id="DOC-ABCD-1",
                    source_type=SourceType.press_release,
                    title="ABCD release",
                    fetched_at=now,
                    local_path=str(raw_dir / "docs" / "ABCD" / "DOC-ABCD-1.txt"),
                ),
                Source(
                    source_id="RAW-JSON",
                    source_type=SourceType.ctgov,
                    fetched_at=now,
                    local_path=str(raw_dir / "ctgov.json"),
                ),
                Source(
                    source_id="ESCAPE",
                    source_type=SourceType.other,
                    fetched_at=now,
                    local_path=str(raw_dir / ".." / "secret.txt"),
                ),
                Source(source_id="MNC-1", source_type=SourceType.mnc_material, fetched_at=now),
            ]
        )
        target = Target(ticker="ABCD", name="Abcd Bio", shortlisted=True)
        buyer = Buyer(ticker="PFE", name="Pfizer", buy_rationale="Needs obesity assets")
        s.add_all([target, buyer])
        s.flush()
        program = Program(target_id=target.id, name="ABC-101", mechanism="GLP-1 agonist")
        bare = Program(target_id=target.id, name="ABC-202")
        pref = BuyerPreference(
            buyer_id=buyer.id, dimension="therapeutic_area", rank=1, label="肥胖"
        )
        s.add_all([program, bare, pref])
        s.flush()
        pi = ProgramIndication(
            program_id=program.id,
            indication="Obesity",
            therapeutic_area="obesity_metabolic",
            stage=Stage.phase2,
        )
        match = Match(buyer_id=buyer.id, target_id=target.id, score=3.0, rationale="肥胖")
        s.add_all([pi, match])
        s.flush()
        trial = Trial(
            nct_id="NCT00000001",
            target_id=target.id,
            indication_id=pi.id,
            title="ABC-101 in obesity",
            phase=Stage.phase2,
            enrollment=120,
            enrollment_type="ESTIMATED",
        )
        s.add(trial)
        s.flush()
        result = TrialResult(trial_id=trial.id, endpoint="Weight change", result="-12%")
        s.add(result)
        s.flush()
        s.add_all(
            [
                claim(buyer, "buy_rationale", "MNC-1", "Needs obesity assets"),
                claim(pref, "label", "MNC-1", "肥胖"),
                claim(match, "score", "MNC-1", "3.0", kind=ClaimKind.inference,
                      confidence=Confidence.medium, produced_by=ProducedBy.manual),
                claim(program, "mechanism", "DOC-ABCD-1", "GLP-1 agonist",
                      produced_by=ProducedBy.llm, model="deepseek-chat",
                      quote="ABC-101 is a GLP-1 agonist."),
                claim(pi, "stage", "CTG-NCT00000001", "phase2", kind=ClaimKind.inference,
                      confidence=Confidence.high),
                claim(trial, "title", "CTG-NCT00000001", "ABC-101 in obesity"),
                claim(trial, "enrollment", "CTG-NCT00000001", "120"),
                claim(result, "result", "CTG-NCT00000001", "-12%"),
            ]
        )  # fmt: skip
        s.commit()
    return db_path


@pytest.fixture
def client(seeded, raw_dir, tmp_path):
    return TestClient(create_app(db_path=seeded, web_dist=tmp_path / "no-dist", raw_dir=raw_dir))


def test_claims_land_on_their_entity_and_field(seeded):
    with Session(rw_engine(seeded)) as s:
        detail = views.target_detail(s, "abcd")
    abc, bare = detail.programs
    mech = abc.sources["mechanism"]
    assert [c.produced_by for c in mech] == ["llm"]
    assert mech[0].model == "deepseek-chat" and mech[0].quote == "ABC-101 is a GLP-1 agonist."
    assert mech[0].source.source_id == "DOC-ABCD-1" and mech[0].source.title == "ABCD release"
    stage = abc.indications[0].sources["stage"]
    assert stage[0].kind == "inference" and stage[0].confidence == "high"
    assert bare.sources == {} and abc.sources.get("modality", []) == []
    assert set(detail.results[0].sources) == {"result"}


def test_buyer_detail(client):
    body = client.get("/api/buyers/pfe").json()
    assert body["buyer"]["sources"]["buy_rationale"][0]["source"]["source_id"] == "MNC-1"
    assert body["preferences"][0]["label"] == "肥胖"
    match = body["matches"][0]
    assert match["ticker"] == "ABCD" and match["shortlisted"]
    assert match["sources"]["score"][0]["confidence"] == "medium"
    summary = client.get("/api/buyers").json()[0]
    assert summary["preferences"] == 1 and summary["therapeutic_areas"] == ["肥胖"]
    assert summary["loe"] == []
    assert client.get("/api/buyers/XXX").status_code == 404


def test_company_detail_lists_trial_summaries(client):
    body = client.get("/api/targets/ABCD").json()
    trial = body["trials"][0]
    assert trial["source_ids"] == ["CTG-NCT00000001"] and trial["results"] == 1
    assert "sources" not in trial
    assert body["results"][0]["nct_id"] == "NCT00000001"
    assert client.get("/api/targets/ZZZZ").status_code == 404


def test_trial_detail(client):
    body = client.get("/api/trials/nct00000001").json()
    assert body["ticker"] == "ABCD" and body["asset"] == "ABC-101"
    assert body["trial"]["enrollment_type"] == "ESTIMATED"
    assert body["trial"]["sources"]["enrollment"][0]["value"] == "120"
    assert body["indication"]["sources"]["stage"][0]["kind"] == "inference"
    assert body["results"][0]["result"] == "-12%"
    assert client.get("/api/trials/NCT99999999").status_code == 404


def test_source_with_archived_text(client):
    meta = client.get("/api/sources/DOC-ABCD-1").json()
    assert meta["has_text"] and meta["claims"] == 1
    assert datetime.fromisoformat(meta["fetched_at"]).tzinfo is not None
    resp = client.get("/api/sources/DOC-ABCD-1/text")
    assert resp.status_code == 200 and resp.text == "ABC-101 is a GLP-1 agonist."
    assert resp.headers["content-type"].startswith("text/plain")


@pytest.mark.parametrize("source_id", ["RAW-JSON", "ESCAPE", "MNC-1"])
def test_text_refused_outside_raw_dir_or_not_txt(client, source_id):
    assert not client.get(f"/api/sources/{source_id}").json()["has_text"]
    assert client.get(f"/api/sources/{source_id}/text").status_code == 404


def test_unknown_source(client):
    assert client.get("/api/sources/NOPE").status_code == 404
    assert client.get("/api/sources/NOPE/text").status_code == 404


def test_deep_link_serves_index_but_unknown_api_is_404(seeded, tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<div id=root></div>")
    (dist / "assets" / "app.js").write_text("console.log(1)")
    client = TestClient(create_app(db_path=seeded, web_dist=dist))
    assert "root" in client.get("/targets/ABCD").text
    assert "console" in client.get("/assets/app.js").text
    assert client.get("/api").status_code == 404
    unknown = client.get("/api/nope")
    assert unknown.status_code == 404 and "root" not in unknown.text


# --- committed snapshot ---------------------------------------------------------------------

needs_snapshot = pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")


@pytest.fixture(scope="module")
def snap():
    return TestClient(create_app(db_path=SNAPSHOT, web_dist=Path("no-dist")))


@needs_snapshot
def test_vktx_from_snapshot(snap):
    body = snap.get("/api/targets/VKTX").json()
    vk2735 = next(p for p in body["programs"] if p["name"] == "VK2735")
    assert any(i["stage"] == "phase3" for i in vk2735["indications"])
    llm = vk2735["sources"]["mechanism"][0]
    assert llm["produced_by"] == "llm" and llm["quote"] and llm["model"]
    assert llm["source"]["source_id"].startswith(("DOC-", "MAN-"))
    assert body["catalysts"] and body["financial"]["market_cap"]
    primary = body["recommendations"][0]
    assert primary["is_primary"] and primary["thesis"]


@needs_snapshot
def test_shortlist_therapeutic_area_from_snapshot(snap):
    items = snap.get("/api/shortlist").json()["items"]
    vktx = next(i for i in items if i["ticker"] == "VKTX")
    assert vktx["therapeutic_area"] and vktx["buyer_ticker"]


@needs_snapshot
def test_rgnx_llm_result_quote_is_in_archived_text(snap):
    body = snap.get("/api/targets/RGNX").json()
    llm = [
        c
        for r in body["results"]
        for claims in r["sources"].values()
        for c in claims
        if c["produced_by"] == "llm"
    ]
    assert llm
    text = snap.get(f"/api/sources/{llm[0]['source']['source_id']}/text").text
    assert " ".join(llm[0]["quote"].split())[:40] in " ".join(text.split())


@needs_snapshot
def test_shortlisted_companies_hold_the_top_ranks(snap):
    # The page ranking and the shortlist must agree, ties included.
    items = snap.get("/api/shortlist").json()["items"]
    picked = sorted(i["rank"] for i in items if i["shortlisted"])
    assert picked == list(range(1, len(picked) + 1))
