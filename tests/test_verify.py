from pathlib import Path

import pytest
from sqlmodel import Session

from intel import verify
from intel.db import ro_engine

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "processed" / "intel.db"
pytestmark = pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")


def ids(rows):
    return [r.claim.id for r in rows]


def test_same_seed_same_sample():
    with Session(ro_engine(SNAPSHOT)) as s:
        first, again = verify.sample(s, 6), verify.sample(s, 6)
        other = verify.sample(s, 6, seed=1)
    assert ids(first) == ids(again) and ids(first) != ids(other)
    assert {r.layer for r in first} == {"structured", "review", "llm"}


def test_auto_check_flags_a_changed_value():
    with Session(ro_engine(SNAPSHOT)) as s:
        rows = [r for r in verify.sample(s, 8) if r.layer == "structured"]
        verify.auto_check(s, rows, ROOT / "data" / "raw")
        assert {r.auto_check for r in rows} == {"一致"}
        with s.no_autoflush:
            for r in rows:
                r.claim.value = "1" if r.claim.field != "title" else "tampered"
            verify.auto_check(s, rows, ROOT / "data" / "raw")
        s.rollback()
    assert {r.auto_check for r in rows} == {"不一致"}


def test_spot_check_lists_five_signed_reviews():
    with Session(ro_engine(SNAPSHOT)) as s:
        text = verify.spot_check(ROOT / "data" / "manual" / "reviews", s)
    assert text.count("\n## ") == 5 and "结果：" in text
