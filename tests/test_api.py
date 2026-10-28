from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

from intel.api import create_app
from intel.db import ro_engine
from intel.models import DOMAIN_TABLES, Target


@pytest.fixture
def client(db_path, tmp_path):
    return TestClient(create_app(db_path=db_path, web_dist=tmp_path / "no-dist"))


def test_write_through_runtime_connection_fails(db_path):
    before = db_path.read_bytes()
    with Session(ro_engine(db_path)) as session:
        session.add(Target(ticker="ABCD", name="Abcd"))
        with pytest.raises(OperationalError, match="readonly"):
            session.commit()
    assert db_path.read_bytes() == before


def test_missing_snapshot_names_the_path(tmp_path):
    missing = tmp_path / "nope.db"
    with pytest.raises(FileNotFoundError, match="nope.db"):
        create_app(db_path=missing)


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200 and resp.json() == {"status": "ok"}


def test_meta_on_empty_snapshot(client):
    body = client.get("/api/meta").json()
    assert datetime.fromisoformat(body["generated_at"]) <= datetime.now(UTC)
    assert body["counts"] == {m.__tablename__: 0 for m in DOMAIN_TABLES}


def test_frontend_is_served_same_origin(db_path, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<div id=root></div>")
    client = TestClient(create_app(db_path=db_path, web_dist=dist))
    assert "root" in client.get("/").text
    assert client.get("/api/health").status_code == 200
