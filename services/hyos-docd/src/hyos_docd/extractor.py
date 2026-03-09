"""
hyos-docd — text extraction from documents

Supports:
  - Plain text / Markdown: direct read
  - PDF: pdftotext (poppler-utils, dnf install poppler-utils)
  - DOCX: zip + XML parse (no deps)
  - ODT: zip + XML parse (no deps)
  - HTML: strip tags

All extraction is read-only. No subprocess is allowed to write to the filesystem.
Input is validated against the allowed paths before extraction.
"""

import logging
import re
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import urlparse, unquote
from xml.etree import ElementTree

log = logging.getLogger(__name__)

ALLOWED_ROOTS = [
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
]

MAX_TEXT_CHARS = 32_000  # ~8k tokens; enough for most letters/documents


def _is_allowed(path: Path) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(root) for root in ALLOWED_ROOTS)


def uri_to_path(uri: str) -> Path:
    """Convert a file:// URI to an absolute Path. Raises ValueError if not file://."""
    parsed = urlparse(str(uri))
    if parsed.scheme != "file":
        raise ValueError(f"Only file:// URIs are accepted, got: {uri!r}")
    return Path(unquote(parsed.path))


def extract_text(uri: str) -> str:
    """
    Extract plain text from a document URI.
    Raises PermissionError if the path is outside allowed directories.
    Raises ValueError for unsupported URI schemes.
    """
    path = uri_to_path(uri)

    if not _is_allowed(path):
        raise PermissionError(f"Path outside allowed directories: {path}")

    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        text = _read_plain(path)
    elif suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".docx":
        text = _read_docx(path)
    elif suffix == ".odt":
        text = _read_odt(path)
    elif suffix in (".html", ".htm"):
        text = _read_html(path)
    else:
        # For unknown types, return just the filename as a hint
        text = f"[File: {path.name}]"

    return text[:MAX_TEXT_CHARS]


def _read_plain(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise RuntimeError(f"Cannot read {path}: {e}") from e


def _read_pdf(path: Path) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
        log.warning("pdftotext returned %d for %s", result.returncode, path)
    except FileNotFoundError:
        log.warning("pdftotext not found. Install poppler-utils: dnf install poppler-utils")
    except subprocess.TimeoutExpired:
        log.warning("pdftotext timed out for %s", path)
    except OSError as e:
        log.warning("pdftotext error for %s: %s", path, e)
    return ""


def _read_docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            with z.open("word/document.xml") as f:
                tree = ElementTree.parse(f)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts = []
        for para in tree.findall(".//w:p", ns):
            text = "".join(t.text or "" for t in para.findall(".//w:t", ns))
            if text.strip():
                parts.append(text)
        return "\n".join(parts)
    except Exception as e:
        log.warning("DOCX parse error for %s: %s", path, e)
        return ""


def _read_odt(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            with z.open("content.xml") as f:
                tree = ElementTree.parse(f)
        # Strip all XML tags, join text nodes
        raw = ElementTree.tostring(tree.getroot(), encoding="unicode", method="text")
        return re.sub(r"\s+", " ", raw).strip()
    except Exception as e:
        log.warning("ODT parse error for %s: %s", path, e)
        return ""


def _read_html(path: Path) -> str:
    raw = _read_plain(path)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", text).strip()
