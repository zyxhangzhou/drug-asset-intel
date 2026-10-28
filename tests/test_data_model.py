from datetime import UTC, datetime

import pytest
from sqlalchemy import inspect
from sqlmodel import Session, select

from intel.db import (
    IntegrityViolation,
    archive_matches,
    archived_source,
    init_db,
    provenance_gaps,
    rw_engine,
)
from intel.enums import ClaimKind, Confidence, ProducedBy, SourceType, Stage
from intel.models import (
    DOMAIN_TABLES,
    Claim,
    Program,
    ProgramIndication,
    Source,
    Target,
    Trial,
)


def claim(**overrides):
    base = dict(
        entity_type="trial",
        entity_id="1",
        field="enrollment_target",
        value="120",
        kind=ClaimKind.fact,
        source_id="CTG-NCT00000001",
        produced_by=ProducedBy.api,
    )
    return Claim(**(base | overrides))


# --- entities -------------------------------------------------------------------------


def test_fresh_database_has_every_entity_table(db_path):
    tables = set(inspect(rw_engine(db_path)).get_table_names())
    assert {m.__tablename__ for m in DOMAIN_TABLES} | {"source", "claim", "snapshot_meta"} <= tables


def test_init_db_is_rerunnable_and_keeps_data(db_path, session):
    session.add(Target(ticker="ABCD", name="Abcd Therapeutics"))
    session.commit()
    init_db(db_path)
    with Session(rw_engine(db_path)) as again:
        assert again.exec(select(Target.ticker)).all() == ["ABCD"]


def test_pipeline_hierarchy_is_navigable(session):
    target = Target(ticker="ABCD", name="Abcd Therapeutics")
    program = Program(target=target, name="ABC-101")
    indication = ProgramIndication(program=program, indication="NSCLC", stage=Stage.phase2)
    trial = Trial(nct_id="NCT00000001", indication=indication)
    session.add(trial)
    session.commit()

    loaded = session.exec(select(Target)).one()
    assert loaded.programs[0].indications[0].trials[0].nct_id == "NCT00000001"
    assert session.exec(select(Trial)).one().indication.program.target.ticker == "ABCD"


# --- sources --------------------------------------------------------------------------


def test_source_keeps_external_identifier(session):
    session.add(
        Source(
            source_id="MRK-1",
            source_type=SourceType.mnc_material,
            url="https://www.merck.com/news/",
            published_date=datetime(2026, 8, 1).date(),
            fetched_at=datetime.now(UTC),
        )
    )
    session.commit()
    assert session.get(Source, "MRK-1").url == "https://www.merck.com/news/"


def test_unknown_publish_date_still_requires_fetch_time(session):
    session.add(Source(source_id="X-1", source_type=SourceType.other, fetched_at=datetime.now(UTC)))
    session.commit()
    src = session.get(Source, "X-1")
    assert src.published_date is None and src.fetched_at is not None


def test_archived_document_hash_is_verifiable(tmp_path, session):
    doc = tmp_path / "8k-ex99.htm"
    doc.write_text("<p>Topline results</p>")
    session.add(archived_source("SEC-8K-1", SourceType.sec_filing, doc))
    session.commit()

    src = session.get(Source, "SEC-8K-1")
    assert src.content_hash and archive_matches(src)
    doc.write_text("tampered")
    assert not archive_matches(src)


# --- claims ---------------------------------------------------------------------------


def test_fact_claim_from_api(session, source):
    session.add(claim())
    session.commit()
    assert session.exec(select(Claim)).one().kind == ClaimKind.fact


def test_claim_must_reference_registered_source(session):
    session.add(claim(source_id="NOPE-1"))
    with pytest.raises(IntegrityViolation, match="unregistered source"):
        session.commit()


def test_inference_requires_confidence(session, source):
    session.add(claim(kind=ClaimKind.inference, produced_by=ProducedBy.manual))
    with pytest.raises(IntegrityViolation, match="confidence"):
        session.commit()


def test_inference_with_confidence_passes(session, source):
    session.add(claim(kind=ClaimKind.inference, confidence=Confidence.medium))
    session.commit()


def test_llm_claim_requires_quote(session, source):
    session.add(claim(produced_by=ProducedBy.llm, model="deepseek-chat", quote="  "))
    with pytest.raises(IntegrityViolation, match="quote"):
        session.commit()


def test_llm_claim_with_quote_passes(session, source):
    session.add(
        claim(produced_by=ProducedBy.llm, model="deepseek-chat", quote="enrolled 120 patients")
    )
    session.commit()


# --- vocabularies ---------------------------------------------------------------------


def test_out_of_vocabulary_stage_is_rejected(session):
    target = Target(ticker="ABCD", name="Abcd")
    program = Program(target=target, name="ABC-101")
    session.add(ProgramIndication(program=program, indication="NSCLC", stage="Ph III"))
    with pytest.raises(IntegrityViolation, match="phase3"):
        session.commit()


def test_vocabulary_string_value_is_accepted(session):
    target = Target(ticker="ABCD", name="Abcd")
    program = Program(target=target, name="ABC-101")
    session.add(ProgramIndication(program=program, indication="NSCLC", stage="phase3"))
    session.commit()
    assert session.exec(select(ProgramIndication)).one().stage == Stage.phase3


# --- provenance check -----------------------------------------------------------------


def test_unsupported_value_is_a_gap(session, source):
    session.add(Target(ticker="ABCD", name="Abcd", selection_rationale="fits MRK oncology"))
    session.commit()
    assert provenance_gaps(session) == [("target", "1", "selection_rationale")]


def test_claimed_value_is_not_a_gap(session, source):
    session.add(Target(ticker="ABCD", name="Abcd", selection_rationale="fits MRK oncology"))
    session.add(
        claim(
            entity_type="target",
            field="selection_rationale",
            kind=ClaimKind.inference,
            confidence=Confidence.medium,
            produced_by=ProducedBy.manual,
        )
    )
    session.commit()
    assert provenance_gaps(session) == []


def test_empty_value_is_not_a_gap(session):
    session.add(Target(ticker="ABCD", name="Abcd", selection_rationale=None, cik=""))
    session.commit()
    assert provenance_gaps(session) == []
