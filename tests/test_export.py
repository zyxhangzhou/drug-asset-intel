import re
from pathlib import Path

import pytest
from openpyxl import load_workbook
from sqlmodel import Session

from intel.db import ro_engine
from intel.export import export

SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "processed" / "intel.db"
pytestmark = pytest.mark.skipif(not SNAPSHOT.exists(), reason="snapshot not built")
SOURCE_ID = re.compile(r"([^;（]+)（")


def write(tmp: Path, name: str) -> Path:
    with Session(ro_engine(SNAPSHOT)) as s:
        return export(s, tmp / name, outputs_dir=SNAPSHOT.parent)


def cells(path: Path) -> dict[str, list[tuple]]:
    wb = load_workbook(path, read_only=True)
    return {ws.title: list(ws.iter_rows(values_only=True)) for ws in wb}


@pytest.fixture(scope="module")
def book(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("export")
    return cells(write(tmp, "a.xlsx")), tmp


def rows_of(sheet: list[tuple]) -> list[dict]:
    header, *rows = sheet
    return [dict(zip(header, r, strict=True)) for r in rows]


def test_same_snapshot_same_contents(book):
    first, tmp = book
    assert cells(write(tmp, "b.xlsx")) == first


def test_every_cited_source_is_listed(book):
    sheets, _ = book
    listed = {r["来源 ID"] for r in rows_of(sheets["来源"])}
    cited = set()
    for title in ("候选公司", "管线", "临床数据", "催化事件"):
        for row in rows_of(sheets[title]):
            for key, value in row.items():
                if key.endswith("来源") and value:
                    cited.update(m.strip() for m in SOURCE_ID.findall(value))
    assert cited and cited <= listed


def test_status_counts_cover_every_company(book):
    sheets, _ = book
    companies = rows_of(sheets["候选公司"]) + rows_of(sheets["其余评估公司"])
    counts = [
        int(re.search(r"(\d+) 家", r[0]).group(1)) for r in sheets["说明"] if r[0] and "家" in r[0]
    ]
    assert len(counts) == 3 and sum(counts) == len(companies)


def test_main_sheet_holds_only_the_shortlist(book):
    sheets, _ = book
    picked = {r["代码"] for r in rows_of(sheets["候选公司"])}
    rest = rows_of(sheets["其余评估公司"])
    assert 20 <= len(picked) <= 30 and not picked & {r["代码"] for r in rest}
    assert all(r["未入选原因"] for r in rest)
    for title in ("管线", "临床数据", "催化事件"):
        assert {r["代码"] for r in rows_of(sheets[title])} <= picked


def test_shortlisted_row_has_thesis_and_financials(book):
    sheets, _ = book
    vktx = next(r for r in rows_of(sheets["候选公司"]) if r["代码"] == "VKTX")
    assert vktx["推荐逻辑（入选理由）"] and vktx["推荐逻辑来源"]
    assert vktx["市值（百万美元）"] and "NASDAQ-VKTX" in vktx["市值来源"]
    assert vktx["收购成本下限（百万美元）"] and "MAN-PREM-" in vktx["收购成本来源"]
    catalysts = [r for r in rows_of(sheets["催化事件"]) if r["代码"] == "VKTX"]
    assert {r["出处"] for r in catalysts} >= {"推荐方向的下一事件", "CT.gov 预计主要完成日（推断）"}
