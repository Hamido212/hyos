"""
hyos-indexerd — file system scanner

Walks the allowed paths and extracts text content for indexing.
Plain text and markdown are read directly.
PDFs are converted via `pdftotext` (poppler-utils, available on Fedora).
DOCX is parsed via the zip+XML structure (no extra dependency).
Everything else is indexed by filename only.
"""

import logging
import subprocess
import threading
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .db import IndexDB, doc_id_for_path, mimetype_for_path
from .xdg import get_allowed_roots

log = logging.getLogger(__name__)

# Resolved at import time so the list is stable for the lifetime of the process.
# Uses ~/.config/user-dirs.dirs so German/French/etc. installs work correctly.
ALLOWED_ROOTS: list[Path] = get_allowed_roots()

INDEXED_SUFFIXES = {".txt", ".md", ".pdf", ".docx", ".odt", ".html", ".htm"}


def _extract_text_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _extract_text_pdf(path: Path) -> str:
    """Use pdftotext (poppler-utils). Falls back to filename-only on failure."""
    try:
        result = subprocess.run(
            ["pdftotext", "-", "-"],
            input=path.read_bytes(),
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        log.debug("pdftotext failed for %s: %s", path, e)
    return ""


def _extract_text_docx(path: Path) -> str:
    """Parse DOCX as a ZIP file and extract paragraph text from document.xml."""
    try:
        with zipfile.ZipFile(path) as z:
            with z.open("word/document.xml") as f:
                tree = ElementTree.parse(f)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for para in tree.findall(".//w:p", ns):
            text = "".join(t.text or "" for t in para.findall(".//w:t", ns))
            if text.strip():
                paragraphs.append(text)
        return "\n".join(paragraphs)
    except Exception as e:
        log.debug("DOCX extraction failed for %s: %s", path, e)
        return ""


def _extract_text(path: Path, mimetype: str) -> str:
    if mimetype in ("text/plain", "text/markdown"):
        return _extract_text_txt(path)
    if mimetype == "application/pdf":
        return _extract_text_pdf(path)
    if "wordprocessingml" in mimetype:
        return _extract_text_docx(path)
    if mimetype in ("text/html",):
        # Strip HTML tags naively; good enough for FTS
        raw = _extract_text_txt(path)
        import re
        return re.sub(r"<[^>]+>", " ", raw)
    return ""  # Index by filename only


def _is_within_allowed(path: Path) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(root) for root in ALLOWED_ROOTS)


class Scanner:

    def __init__(self, db: IndexDB) -> None:
        self._db = db
        self._lock = threading.Lock()
        self._scanning = False

    def scan_path(self, root: Path, recursive: bool = True, on_done=None) -> None:
        """Start a background scan of root. Thread-safe."""
        if not _is_within_allowed(root):
            log.warning("Scan requested for disallowed path: %s", root)
            return

        def _run():
            with self._lock:
                self._scanning = True
            added = updated = errors = 0
            try:
                paths = root.rglob("*") if recursive else root.glob("*")
                for p in paths:
                    if p.is_file() and p.suffix.lower() in INDEXED_SUFFIXES:
                        try:
                            self._index_file(p)
                            added += 1
                        except Exception as e:
                            log.warning("Error indexing %s: %s", p, e)
                            errors += 1
            finally:
                with self._lock:
                    self._scanning = False
                log.info("Scan done: root=%s added=%d errors=%d", root, added, errors)
                if on_done:
                    on_done({"added": added, "updated": updated, "errors": errors})

        thread = threading.Thread(target=_run, daemon=True, name=f"scan-{root.name}")
        thread.start()

    def _index_file(self, path: Path) -> None:
        try:
            stat = path.stat()
        except OSError:
            return
        doc_id = doc_id_for_path(path)
        uri = path.resolve().as_uri()
        mimetype = mimetype_for_path(path)
        mtime = int(stat.st_mtime)
        size = stat.st_size
        text = _extract_text(path, mimetype)
        self._db.upsert(doc_id, uri, path.name, mimetype, mtime, size, text)

    def initial_scan(self) -> None:
        """Trigger background scan of all allowed roots that exist."""
        for root in ALLOWED_ROOTS:
            if root.exists():
                log.info("Starting initial scan: %s", root)
                self.scan_path(root, recursive=True)
