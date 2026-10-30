"""Chunks of archived document text and an FTS5 index over them (a rebuildable local file)."""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

CHUNK_CHARS = 6000
OVERLAP_CHARS = 600
WHOLE_DOC_CHARS = 12000


@dataclass(frozen=True)
class Chunk:
    source_id: str
    no: int
    start: int
    end: int
    text: str


def chunk_text(source_id: str, text: str) -> list[Chunk]:
    """Paragraph-aligned chunks of about CHUNK_CHARS; consecutive chunks overlap."""
    if len(text) <= WHOLE_DOC_CHARS:
        return [Chunk(source_id, 0, 0, len(text), text)]
    breaks = [m.end() for m in re.finditer(r"\n", text)] + [len(text)]
    chunks, start = [], 0
    while start < len(text):
        limit = start + CHUNK_CHARS
        end = max((b for b in breaks if start < b <= limit), default=min(limit, len(text)))
        chunks.append(Chunk(source_id, len(chunks), start, end, text[start:end]))
        if end >= len(text):
            break
        back = end - OVERLAP_CHARS
        start = max((b for b in breaks if start < b <= back), default=end)
    return chunks


class ChunkIndex:
    def __init__(self, path: Path | str):
        if isinstance(path, Path):
            path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5("
            "text, source_id UNINDEXED, no UNINDEXED, start UNINDEXED, end UNINDEXED, "
            "text_sha256 UNINDEXED)"
        )

    def add(self, source_id: str, text: str, text_sha256: str) -> list[Chunk]:
        """Index a document unless the same text is already indexed."""
        row = self.db.execute(
            "SELECT text_sha256 FROM chunks WHERE source_id = ? LIMIT 1", (source_id,)
        ).fetchone()
        chunks = chunk_text(source_id, text)
        if row and row[0] == text_sha256:
            return chunks
        self.db.execute("DELETE FROM chunks WHERE source_id = ?", (source_id,))
        self.db.executemany(
            "INSERT INTO chunks (text, source_id, no, start, end, text_sha256) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(c.text, c.source_id, c.no, c.start, c.end, text_sha256) for c in chunks],
        )
        self.db.commit()
        return chunks

    def search(self, source_id: str, query: str, k: int = 4) -> list[Chunk]:
        """Best-matching chunks of one document, returned in document order."""
        rows = self.db.execute(
            "SELECT source_id, no, start, end, text FROM chunks "
            "WHERE chunks MATCH ? AND source_id = ? ORDER BY bm25(chunks) LIMIT ?",
            (query, source_id, k),
        ).fetchall()
        hits = [Chunk(r[0], int(r[1]), int(r[2]), int(r[3]), r[4]) for r in rows]
        return sorted(hits, key=lambda c: c.no)

    def close(self) -> None:
        self.db.close()
