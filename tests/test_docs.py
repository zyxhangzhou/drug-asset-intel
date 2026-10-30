import json
from pathlib import Path

import httpx
import pytest

from intel.config import Settings
from intel.docs.documents import COLUMNS, generated_id, read_documents
from intel.docs.fetch import fetch_documents, parse_index
from intel.docs.index import CHUNK_CHARS, ChunkIndex, chunk_text
from intel.docs.text import html_to_text, normalize, numbers, pdf_to_text, to_text
from intel.enums import SourceType
from intel.fetch import MissingConfig

FIXTURES = Path(__file__).parent / "fixtures" / "docs"


def settings(ua: str | None = "Test test@example.com") -> Settings:
    return Settings(Path("x.db"), Path("dist"), ua, None, None, None, None, None, None)


# --- text -----------------------------------------------------------------------------


def test_html_drops_inline_xbrl_header_and_keeps_table_rows():
    raw = (
        "<html><ix:header><ix:hidden>dei:Secret 123</ix:hidden></ix:header>"
        "<p>Primary endpoint met.</p><table><tr><td>Arm</td><td>ORR</td></tr>"
        "<tr><td>A</td><td>42%</td></tr></table><script>var x=1</script></html>"
    )
    text = html_to_text(raw)
    assert "Secret" not in text and "var x" not in text
    assert text.splitlines() == ["Primary endpoint met.", "Arm | ORR |", "A | 42% |"]
    assert html_to_text(raw) == text  # deterministic


def test_pdf_text_has_page_markers():
    text = pdf_to_text((FIXTURES / "sample.pdf").read_bytes())
    assert text == "[page 1]\nTopline data expected in 2H 2027."
    assert to_text((FIXTURES / "sample.pdf").read_bytes(), "application/octet-stream") == text


def test_empty_pdf_gives_empty_text():
    import io

    from pypdf import PdfWriter

    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.write(buf)
    assert to_text(buf.getvalue(), "application/pdf") == ""


def test_normalize_quotes_dashes_space_case():
    a = "The trial “met” its primary\n endpoint – p<0.001"
    b = 'the trial "met" its primary endpoint - P<0.001'
    assert normalize(a) == normalize(b)


def test_numbers_ignore_thousands_and_trailing_zeros():
    assert numbers("1,234 patients, 42.50% and -3.0") == {"1234", "42.5", "3"}


# --- document list --------------------------------------------------------------------


def write_list(path: Path, rows: list[dict]) -> Path:
    import csv

    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return path


def row(**kw) -> dict:
    base = dict(ticker="VKTX", url="https://www.sec.gov/a.htm", source_type="press_release",
                title="PR", published_date="2026-08", source_id="", note="")  # fmt: skip
    return base | kw


def test_document_list_validates_rows(tmp_path):
    path = write_list(
        tmp_path / "documents.csv",
        [
            row(),
            row(url="ftp://x/y"),
            row(source_type="market_data", url="https://b"),
            row(url="https://c", source_id="MAN-VKTX-2"),
        ],
    )
    docs, errors = read_documents(path)
    assert [d.source_id for d in docs] == [generated_id("VKTX", "https://www.sec.gov/a.htm"),
                                           "MAN-VKTX-2"]  # fmt: skip
    assert [line for line, _ in errors] == [3, 4]
    assert docs[0].source_type is SourceType.press_release


def test_generated_id_is_stable():
    assert generated_id("VKTX", "https://x/a") == generated_id("VKTX", "https://x/a")
    assert generated_id("VKTX", "https://x/a").startswith("DOC-VKTX-")
    assert generated_id("VKTX", "https://x/a") != generated_id("VKTX", "https://x/b")


# --- fetch ----------------------------------------------------------------------------


def transport(routes: dict[str, httpx.Response], seen: list) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((str(request.url), request.headers.get("user-agent")))
        return routes[str(request.url)]

    return httpx.MockTransport(handler)


def test_fetch_archives_text_and_hashes_then_skips_cached(tmp_path):
    docs, _ = read_documents(
        write_list(
            tmp_path / "d.csv",
            [row(), row(url="https://ir.example.com/x", source_type="company_ir")],
        )
    )
    seen: list = []
    routes = {
        "https://www.sec.gov/a.htm": httpx.Response(
            200, headers={"content-type": "text/html"}, text="<p>Hello world</p>"
        ),
        "https://ir.example.com/x": httpx.Response(403),
    }
    with httpx.Client(transport=transport(routes, seen)) as client:
        result = fetch_documents(docs, client, settings(), tmp_path / "docs")
        assert result.fetched == [docs[0].source_id]
        assert result.failed == {docs[1].source_id: "blocked: HTTP 403"}
        meta = docs[0].meta(tmp_path / "docs")
        assert meta["status"] == "ok" and len(meta["text_sha256"]) == 64
        assert docs[0].text(tmp_path / "docs") == "Hello world"
        assert seen[0][1] == "Test test@example.com"  # SEC gets the contact User-Agent
        assert seen[1][1] != "Test test@example.com"
        log = (tmp_path / "docs" / "fetch_log.jsonl").read_text().splitlines()
        assert [json.loads(x)["status"] for x in log] == ["ok", "blocked"]

        seen.clear()
        again = fetch_documents(docs[:1], client, settings(), tmp_path / "docs")
        assert again.skipped == [docs[0].source_id] and seen == []


def test_sec_fetch_needs_user_agent(tmp_path):
    docs, _ = read_documents(write_list(tmp_path / "d.csv", [row()]))
    with httpx.Client(transport=transport({}, [])) as client, pytest.raises(MissingConfig):
        fetch_documents(docs, client, settings(None), tmp_path / "docs")


def test_parse_index_lists_exhibits_without_images():
    exhibits = parse_index((FIXTURES / "edgar_index.html").read_text())
    kinds = [e.kind for e in exhibits]
    assert "EX-99.1" in kinds and "GRAPHIC" not in kinds
    ex991 = next(e for e in exhibits if e.kind == "EX-99.1")
    assert ex991.url.startswith("https://www.sec.gov/Archives/edgar/data/1372514/")
    assert "/ix?doc=" not in exhibits[0].url


# --- chunks ---------------------------------------------------------------------------


def test_short_document_is_one_chunk():
    chunks = chunk_text("S", "short text")
    assert len(chunks) == 1 and chunks[0].text == "short text"


def test_chunks_cover_text_and_overlap():
    text = "\n".join(f"Paragraph {i} " + "word " * 60 for i in range(200))
    chunks = chunk_text("S", text)
    assert chunks[0].start == 0 and chunks[-1].end == len(text)
    for a, b in zip(chunks, chunks[1:], strict=False):
        assert b.start < a.end  # overlap, no hole
        assert a.end - a.start <= CHUNK_CHARS
    assert all(c.text == text[c.start : c.end] for c in chunks)


def test_search_returns_matching_chunks_in_order(tmp_path):
    filler = "\n".join("Revenue discussion " + "lorem " * 80 for _ in range(60))
    text = filler + "\nThe study met its primary endpoint versus placebo.\n" + filler
    index = ChunkIndex(tmp_path / "index.sqlite")
    chunks = index.add("S", text, "h1")
    assert len(chunks) > 3
    hits = index.search("S", '"primary endpoint" OR placebo', k=4)
    assert hits and all("placebo" in h.text for h in hits)
    assert [h.no for h in hits] == sorted(h.no for h in hits)
    assert index.add("S", text, "h1") == chunks  # same text, not re-indexed
    index.close()


def test_every_task_query_is_valid_fts5():
    from intel.extract.tasks import TASKS

    index = ChunkIndex(":memory:")
    index.add("S", "Phase 3 data expected by year-end; primary endpoint met.", "h")
    for task in TASKS.values():
        index.search("S", task.query)  # raises on a syntax error


# --- table records --------------------------------------------------------------------


def test_table_cell_carries_its_headers():
    from intel.docs.text import table_records

    lines = table_records((FIXTURES / "vktx_ex991.html").read_text(encoding="utf-8"))
    assert (
        "[table 2] Change in Body Weight Following 21 Weeks of Once-Weekly Dosing with VK2735 — "
        "Mean percent change from baseline^4,5 | VK2735 15 mg QW (n=14): -16.3%"
    ) in lines
    assert table_records((FIXTURES / "vktx_ex991.html").read_text(encoding="utf-8")) == lines


def test_split_table_keeps_header_and_title():
    from intel.docs.text import table_records

    lines = table_records((FIXTURES / "vktx_ex991.html").read_text(encoding="utf-8"))
    vomiting = [x for x in lines if x.startswith("[table 7]") and "Vomiting" in x]
    assert vomiting and all("Monthly Dosing" in x for x in vomiting)
    assert any("| VK2735 20 mg QM (n=14): " in x for x in vomiting)
    assert not any("Exhibit 99.1 —" in x for x in lines)  # page header is not a title


def test_table_symbols_superscripts_and_spans():
    from intel.docs.text import table_records

    raw = (
        "<p>Dose response</p><table>"
        "<tr><td></td><td><p>Arm A</p><p>(n=10)</p></td><td>Arm B</td></tr>"
        "<tr><td>ORR<sup>a</sup></td><td>40</td><td>%</td><td>25%</td></tr>"
        "<tr><td>Cost</td><td>$</td><td>1,200</td><td>(5</td><td>)</td></tr>"
        "</table>"
    )
    assert table_records(raw) == [
        "[table 1] Dose response — ORR^a | Arm A (n=10): 40%",
        "[table 1] Dose response — ORR^a | Arm B: 25%",
        "[table 1] Dose response — Cost | Arm A (n=10): $1,200",
        "[table 1] Dose response — Cost | Arm B: (5)",
    ]


def test_unrecognized_table_left_as_rows():
    from intel.docs.text import table_records

    raw = "<table><tr><td>2024</td><td>12</td></tr><tr><td>2025</td><td>15</td></tr></table>"
    assert table_records(raw) == []
    text = to_text(raw.encode(), "text/html")
    assert "2024 | 12 |" in text and "Table records" not in text


def test_html_text_appends_table_records_after_body():
    text = to_text((FIXTURES / "vktx_ex991.html").read_bytes(), "text/html")
    body, records = text.split("[Table records", 1)
    assert "met" in body.lower() and "-16.3%" in records


def test_damaged_pdf_gives_empty_text():
    assert to_text(b"%PDF-1.4 truncated", "application/pdf") == ""
