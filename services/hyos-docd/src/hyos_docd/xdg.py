"""
hyos — XDG user-dirs helper (copy kept local to avoid cross-package imports)

Reads the actual document/download/desktop paths from ~/.config/user-dirs.dirs,
which is authoritative on all freedesktop-compliant systems including localized
Fedora installs (e.g. ~/Dokumente instead of ~/Documents).

Falls back to ~/Documents, ~/Downloads, ~/Desktop if the file is missing.
"""

import os
from pathlib import Path


def _parse_user_dirs(path: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return result
    home = Path.home()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"')
        value = value.replace("$HOME", str(home))
        result[key] = Path(os.path.expandvars(value))
    return result


def get_allowed_roots() -> list[Path]:
    """Return the XDG document roots for this user session."""
    user_dirs_file = Path.home() / ".config" / "user-dirs.dirs"
    dirs = _parse_user_dirs(user_dirs_file)

    home = Path.home()
    candidates = [
        dirs.get("XDG_DOCUMENTS_DIR", home / "Documents"),
        dirs.get("XDG_DOWNLOAD_DIR", home / "Downloads"),
        dirs.get("XDG_DESKTOP_DIR", home / "Desktop"),
    ]
    seen: set[Path] = set()
    roots: list[Path] = []
    for p in candidates:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            roots.append(p)
    return roots
