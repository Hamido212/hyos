"""
hyos-indexerd — SQLite + FTS5 document index

Schema:
  docs          — metadata table (doc_id, uri, name, mimetype, mtime, size, indexed)
  docs_fts      — FTS5 virtual table for full-text search over name + text content

doc_id is a stable sha256 of the canonical file path, so it survives content changes
without re-identifying the document.
"""

import hashlib
import logging
import os
import sqlite3
import time
from pathlib import Path


log = logging.getLogger(__name__)

_DB_PATH = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "hyos" / "index" / "docs.db"

_INIT_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS docs (
    doc_id   TEXT PRIMARY KEY,
    uri      TEXT NOT NULL UNIQUE,
    name     TEXT NOT NULL,
    mimetype TEXT NOT NULL DEFAULT 'application/octet-stream',
    mtime    INTEGER NOT NULL DEFAULT 0,
    size     INTEGER NOT NULL DEFAULT 0,
    indexed  INTEGER NOT NULL DEFAULT 0,
    text     TEXT NOT NULL DEFAULT ''
);

CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
    doc_id UNINDEXED,
    name,
    text,
    content=docs,
    content_rowid=rowid
);

CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
    INSERT INTO docs_fts(rowid, doc_id, name, text)
    VALUES (new.rowid, new.doc_id, new.name, new.text);
END;

CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
    INSERT INTO docs_fts(docs_fts, rowid, doc_id, name, text)
    VALUES ('delete', old.rowid, old.doc_id, old.name, old.text);
END;

CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN
    INSERT INTO docs_fts(docs_fts, rowid, doc_id, name, text)
    VALUES ('delete', old.rowid, old.doc_id, old.name, old.text);
    INSERT INTO docs_fts(rowid, doc_id, name, text)
    VALUES (new.rowid, new.doc_id, new.name, new.text);
END;
"""


def doc_id_for_path(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:32]


def mimetype_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".odt": "application/vnd.oasis.opendocument.text",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".htm": "text/html",
    }.get(suffix, "application/octet-stream")


class IndexDB:

    def __init__(self) -> None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_INIT_SQL)
        self._conn.commit()
        log.info("Index DB ready: %s", _DB_PATH)

    def upsert(self, doc_id: str, uri: str, name: str, mimetype: str,
               mtime: int, size: int, text: str) -> None:
        existing = self._conn.execute(
            "SELECT mtime FROM docs WHERE doc_id = ?", (doc_id,)
        ).fetchone()
        if existing and existing["mtime"] == mtime:
            return  # No change
        self._conn.execute(
            """INSERT INTO docs(doc_id, uri, name, mimetype, mtime, size, indexed, text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(doc_id) DO UPDATE SET
                   uri=excluded.uri, name=excluded.name, mimetype=excluded.mimetype,
                   mtime=excluded.mtime, size=excluded.size,
                   indexed=excluded.indexed, text=excluded.text""",
            (doc_id, uri, name, mimetype, mtime, size, int(time.time()), text),
        )
        self._conn.commit()

    def remove(self, doc_id: str) -> None:
        self._conn.execute("DELETE FROM docs WHERE doc_id = ?", (doc_id,))
        self._conn.commit()

    def search(self, query: str, limit: int) -> list[dict]:
        # FTS5 query; escape special chars to avoid parse errors
        safe_query = query.replace('"', '""')
        rows = self._conn.execute(
            """SELECT d.doc_id, d.uri, d.name, d.mimetype, d.mtime, d.size,
                      snippet(docs_fts, 2, '[', ']', '...', 12) AS snippet
               FROM docs_fts
               JOIN docs d ON d.doc_id = docs_fts.doc_id
               WHERE docs_fts MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (safe_query, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_meta(self, doc_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT doc_id, uri, name, mimetype, mtime, size, indexed FROM docs WHERE doc_id = ?",
            (doc_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_snippet(self, doc_id: str, query: str) -> str:
        safe_query = query.replace('"', '""')
        row = self._conn.execute(
            """SELECT snippet(docs_fts, 2, '[', ']', '...', 20) AS snip
               FROM docs_fts
               WHERE docs_fts MATCH ? AND doc_id = ?
               LIMIT 1""",
            (safe_query, doc_id),
        ).fetchone()
        if row:
            return row["snip"]
        # Fallback: return first 200 chars of stored text
        row2 = self._conn.execute(
            "SELECT substr(text, 1, 200) AS snip FROM docs WHERE doc_id = ?", (doc_id,)
        ).fetchone()
        return row2["snip"] if row2 else ""

    def close(self) -> None:
        self._conn.close()
