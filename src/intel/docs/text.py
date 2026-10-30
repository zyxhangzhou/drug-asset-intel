"""Document text: HTML / PDF to plain text, and the one normalisation used to match quotes."""

import html
import io
import re
import unicodedata
from html.parser import HTMLParser

QUOTE_CHARS = str.maketrans({"‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"', "„": '"'})
DASH_RE = re.compile(r"[‐‑‒–—―−]")
SPACE_RE = re.compile(r"\s+")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|ix:header)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", raw)
    raw = re.sub(r"(?i)</t[dh]>", " | ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    lines = (" ".join(line.split()) for line in text.splitlines())
    return "\n".join(line for line in lines if line)


# --- HTML tables, one line per data cell ------------------------------------------------

BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}
SYMBOL_BEFORE = {"$", "(", "€", "£"}
SYMBOL_AFTER = {")", "%", ")%", "%)"}
VALUE_RE = re.compile(r"^[-−–—<>≤≥~$(]*\s*(\d|[-−–—]$|n/?a$|nm$)", re.I)
MAX_TITLE_CHARS = 160
PAGE_FURNITURE = re.compile(
    r"^(exhibit\s+\d+(\.\d+)?|page\s+\d+(\s+of\s+\d+)?|-?\s*\d{1,3}\s*-?)$", re.I
)
TABLE_RECORDS_HEADING = "[Table records: one line per table cell, with its row and column headers]"


class _TableParser(HTMLParser):
    """Rows of cell texts per table, and the short text block just before each table."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[tuple[str | None, list[list[str]]]] = []
        self._stack: list[list[list[str]]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        # Scripts and styles are dropped: (tag, nesting depth).
        self._skip: tuple[str, int] | None = None
        self._text: list[str] = []  # current text block outside tables
        self._last_block = ""
        self._title_for_next: str | None = None

    def handle_starttag(self, tag, attrs):
        if self._skip:
            if tag == self._skip[0]:
                self._skip = (tag, self._skip[1] + 1)
            return
        if tag in ("script", "style"):
            self._skip = (tag, 1)
            return
        style = (dict(attrs).get("style") or "").replace(" ", "").lower()
        raised = "vertical-align:super" in style or (
            "position:relative" in style and "top:-" in style
        )
        if (tag == "sup" or raised) and self._cell is not None:
            # Keep superscripts (footnote marks, m^2) but set them apart from the word.
            self._cell.append("^")
        if tag == "table":
            if not self._stack:
                self._flush_block()
                self._title_for_next = self._last_block or None
            self._stack.append([])
        elif tag == "tr" and self._stack:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag in BLOCK_TAGS:
            if self._cell is not None:
                self._cell.append(" ")
            elif not self._stack:
                self._flush_block()

    def handle_endtag(self, tag):
        if self._skip:
            if tag == self._skip[0]:
                depth = self._skip[1] - 1
                self._skip = (tag, depth) if depth else None
            return
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._stack:
            self._stack[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._stack:
            rows = self._stack.pop()
            if not self._stack:
                self.tables.append((self._title_for_next, rows))
                self._last_block = ""
        elif tag in BLOCK_TAGS and not self._stack:
            self._flush_block()

    def handle_data(self, data):
        if self._skip:
            return
        if self._cell is not None:
            self._cell.append(data)
        elif not self._stack:
            self._text.append(data)

    def _flush_block(self):
        text = " ".join("".join(self._text).split())
        self._text = []
        if text:
            self._last_block = text if len(text) <= MAX_TITLE_CHARS else ""


def _clean_row(cells: list[str]) -> list[str]:
    out: list[str] = []
    pending = ""
    for c in cells:
        if not c:
            continue
        if c in SYMBOL_BEFORE:
            pending += c
            continue
        if c in SYMBOL_AFTER and out:
            out[-1] += c
            continue
        out.append(pending + c)
        pending = ""
    return out


def _is_value(cell: str) -> bool:
    return bool(VALUE_RE.match(cell))


def _is_header(row: list[str]) -> bool:
    return len(row) > 1 and not any(map(_is_value, row[1:]))


def table_records(raw_html: str) -> list[str]:
    """One line per data cell: table number, title, section, row label, column header, value."""
    parser = _TableParser()
    parser.feed(raw_html)
    parser.close()
    lines: list[str] = []
    prev_header: list[str] | None = None
    prev_title: str | None = None
    for number, (before, raw_rows) in enumerate(parser.tables, start=1):
        rows = [r for r in map(_clean_row, raw_rows) if r and not PAGE_FURNITURE.match(r[0])]
        start = next((i for i, r in enumerate(rows) if _is_header(r)), None)
        if start is not None and all(len(r) == 1 for r in rows[:start]):
            title = " ".join(r[0] for r in rows[:start]) or before
            header, i = rows[start], start + 1
            while i < len(rows) and len(rows[i]) == len(header) and _is_header(rows[i]):
                header = [f"{a} {b}" for a, b in zip(header, rows[i], strict=True)]
                i += 1
            body = rows[i:]
        elif prev_header and any(len(r) in (len(prev_header), len(prev_header) + 1) for r in rows):
            # A table split across pages: reuse the header and title of the previous table.
            header, title, body = prev_header, prev_title, rows
        else:
            continue  # no recognisable header: the rows stay in the body text only
        prefix = f"[table {number}] " + (f"{title} — " if title else "")
        section: list[str] = []
        last_single = False
        for r in body:
            if len(r) == 1:
                section = [*section, r[0]] if last_single else [r[0]]
                last_single = True
                continue
            last_single = False
            if len(r) == len(header):
                columns = header[1:]
            elif len(r) == len(header) + 1:
                columns = header
            else:
                continue
            label = " / ".join([*section, r[0]])
            for column, value in zip(columns, r[1:], strict=True):
                lines.append(f"{prefix}{label} | {column}: {value}")
        prev_header, prev_title = header, title
    return lines


def pdf_to_text(data: bytes) -> str:
    from pypdf import PdfReader

    pages = []
    for number, page in enumerate(PdfReader(io.BytesIO(data)).pages, start=1):
        body = (page.extract_text() or "").strip()
        if body:
            pages.append(f"[page {number}]\n{body}")
    return "\n\n".join(pages)


def to_text(data: bytes, content_type: str, url: str = "") -> str:
    """Plain text of a fetched document; empty when nothing can be extracted (scanned PDF)."""
    if "pdf" in content_type or url.lower().endswith(".pdf") or data[:5] == b"%PDF-":
        return pdf_to_text(data)
    decoded = data.decode("utf-8", errors="replace")
    if "html" in content_type or re.search(r"(?i)<(html|body|div|p)\b", decoded[:5000]):
        text = html_to_text(decoded)
        records = table_records(decoded)
        return f"{text}\n\n{TABLE_RECORDS_HEADING}\n" + "\n".join(records) if records else text
    return decoded.strip()


def normalize(s: str) -> str:
    """NFKC, straight quotes, ASCII hyphens, single spaces, casefolded."""
    s = unicodedata.normalize("NFKC", s).translate(QUOTE_CHARS)
    s = DASH_RE.sub("-", s)
    return SPACE_RE.sub(" ", s).strip().casefold()


def numbers(s: str) -> set[str]:
    """Numbers in a text, thousands separators removed and trailing zeros of decimals dropped."""
    found = set()
    for n in NUMBER_RE.findall(re.sub(r"(?<=\d),(?=\d{3})", "", normalize(s))):
        if "." in n:
            n = n.rstrip("0").rstrip(".")
        found.add(n.lstrip("-") or "0")
    return found
