from datetime import UTC, datetime

import pytest
from sqlmodel import Session

from intel.db import init_db
from intel.enums import SourceType
from intel.models import Source


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "intel.db"
    init_db(path)
    return path


@pytest.fixture
def session(db_path):
    from intel.db import rw_engine

    with Session(rw_engine(db_path)) as s:
        yield s


@pytest.fixture
def source(session):
    src = Source(
        source_id="CTG-NCT00000001",
        source_type=SourceType.ctgov,
        url="https://clinicaltrials.gov/study/NCT00000001",
        fetched_at=datetime.now(UTC),
    )
    session.add(src)
    session.commit()
    return src
