"""Document text: HTML / PDF to plain text, and the one normalisation used to match quotes."""

import html
import io
import re
import unicodedata

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
        return html_to_text(decoded)
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
