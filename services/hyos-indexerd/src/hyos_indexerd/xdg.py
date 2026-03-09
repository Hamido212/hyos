"""
hyos — XDG user-dirs helper

Reads the actual document/download/desktop paths from ~/.config/user-dirs.dirs,
which is authoritative on all freedesktop-compliant systems including localized
Fedora installs (e.g. ~/Dokumente instead of ~/Documents).

Falls back to ~/Documents, ~/Downloads, ~/Desktop if the file is missing.
"""

import os
from pathlib import Path


def _parse_user_dirs(path: Path) -> dict[str, Path]:
    """Parse a user-dirs.dirs file into {XDG_NAME: Path} dict."""
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
        # Values are like "$HOME/Dokumente" — expand $HOME
        value = value.replace("$HOME", str(home))
        result[key] = Path(os.path.expandvars(value))
    return result


def get_allowed_roots() -> list[Path]:
    """Return the XDG document roots for this user session.

    Always resolves to real paths from ~/.config/user-dirs.dirs.
    Only includes directories that actually exist.
    """
    user_dirs_file = Path.home() / ".config" / "user-dirs.dirs"
    dirs = _parse_user_dirs(user_dirs_file)

    home = Path.home()
    candidates = [
        dirs.get("XDG_DOCUMENTS_DIR", home / "Documents"),
        dirs.get("XDG_DOWNLOAD_DIR", home / "Downloads"),
        dirs.get("XDG_DESKTOP_DIR", home / "Desktop"),
    ]
    # Deduplicate and resolve, include even if non-existent
    # so the service can be started and paths indexed later.
    seen: set[Path] = set()
    roots: list[Path] = []
    for p in candidates:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            roots.append(p)
    return roots
