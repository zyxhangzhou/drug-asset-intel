from sqlmodel import Session

from intel.cli import main
from intel.db import rw_engine
from intel.models import Target


def test_init_db_twice_succeeds(tmp_path):
    db = tmp_path / "x.db"
    assert main(["init-db", "--db", str(db)]) == 0
    assert main(["init-db", "--db", str(db)]) == 0
    assert db.exists()


def test_check_provenance_reports_gap_and_fails(db_path, capsys):
    with Session(rw_engine(db_path)) as s:
        s.add(Target(ticker="ABCD", name="Abcd", cik="0000000001"))
        s.commit()
    assert main(["check-provenance", "--db", str(db_path)]) == 1
    out = capsys.readouterr().out
    assert "target#1.cik" in out


def test_check_provenance_passes_on_empty_snapshot(db_path):
    assert main(["check-provenance", "--db", str(db_path)]) == 0
