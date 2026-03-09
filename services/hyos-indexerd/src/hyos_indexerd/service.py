"""
hyos-indexerd — D-Bus service implementation (org.hyos.Indexer1)
"""

import logging
import time

import dbus
import dbus.service

from .db import IndexDB, doc_id_for_path
from .scanner import Scanner, ALLOWED_ROOTS, _is_within_allowed

log = logging.getLogger(__name__)


def _sv(val) -> dbus.Variant:
    if isinstance(val, bool):
        return dbus.Variant("b", val)
    if isinstance(val, int):
        return dbus.Variant("t", val)  # uint64 for timestamps/sizes
    if isinstance(val, float):
        return dbus.Variant("d", val)
    return dbus.Variant("s", str(val) if val is not None else "")


class IndexerService(dbus.service.Object):

    def __init__(self, bus: dbus.SessionBus) -> None:
        name = dbus.service.BusName("org.hyos.Indexer1", bus)
        super().__init__(name, "/org/hyos/Indexer")
        self._db = IndexDB()
        self._scanner = Scanner(self._db)
        log.info("IndexerService ready")

    def start_initial_scan(self) -> None:
        """Called from main after the GLib loop starts."""
        self._scanner.initial_scan()

    # ------------------------------------------------------------------ #
    # D-Bus interface: org.hyos.Indexer1                                  #
    # ------------------------------------------------------------------ #

    @dbus.service.method(
        dbus_interface="org.hyos.Indexer1",
        in_signature="sb",
        out_signature="",
    )
    def IndexPath(self, uri: str, recursive: bool) -> None:
        from pathlib import Path
        from urllib.parse import urlparse, unquote
        parsed = urlparse(str(uri))
        path = Path(unquote(parsed.path))
        if not _is_within_allowed(path):
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.AccessDenied",
                f"Path is outside allowed directories: {path}",
            )
        self._scanner.scan_path(path, recursive=bool(recursive))

    @dbus.service.method(
        dbus_interface="org.hyos.Indexer1",
        in_signature="s",
        out_signature="",
    )
    def RemovePath(self, uri: str) -> None:
        from pathlib import Path
        from urllib.parse import urlparse, unquote
        parsed = urlparse(str(uri))
        path = Path(unquote(parsed.path))
        doc_id = doc_id_for_path(path)
        self._db.remove(doc_id)

    @dbus.service.method(
        dbus_interface="org.hyos.Indexer1",
        in_signature="su",
        out_signature="aa{sv}",
    )
    def Search(self, query: str, limit: int) -> list:
        if not query.strip():
            return dbus.Array([], signature="a{sv}")
        rows = self._db.search(str(query), int(limit) or 20)
        results = []
        for r in rows:
            results.append(dbus.Dictionary({
                "doc_id":   _sv(r.get("doc_id", "")),
                "uri":      _sv(r.get("uri", "")),
                "name":     _sv(r.get("name", "")),
                "mimetype": _sv(r.get("mimetype", "")),
                "mtime":    _sv(r.get("mtime", 0)),
                "score":    dbus.Variant("d", 1.0),
                "snippet":  _sv(r.get("snippet", "")),
            }))
        return dbus.Array(results, signature="a{sv}")

    @dbus.service.method(
        dbus_interface="org.hyos.Indexer1",
        in_signature="s",
        out_signature="a{sv}",
    )
    def GetDocumentMeta(self, doc_id: str) -> dict:
        meta = self._db.get_meta(str(doc_id))
        if meta is None:
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.NotFound",
                f"Document not found: {doc_id}",
            )
        return dbus.Dictionary({
            "doc_id":   _sv(meta["doc_id"]),
            "uri":      _sv(meta["uri"]),
            "name":     _sv(meta["name"]),
            "mimetype": _sv(meta["mimetype"]),
            "mtime":    _sv(meta["mtime"]),
            "size":     _sv(meta["size"]),
            "indexed":  _sv(meta["indexed"]),
        })

    @dbus.service.method(
        dbus_interface="org.hyos.Indexer1",
        in_signature="ss",
        out_signature="s",
    )
    def GetSnippet(self, doc_id: str, query: str) -> str:
        return self._db.get_snippet(str(doc_id), str(query))

    # Signals
    @dbus.service.signal(dbus_interface="org.hyos.Indexer1", signature="s")
    def IndexingStarted(self, uri: str) -> None:
        pass

    @dbus.service.signal(dbus_interface="org.hyos.Indexer1", signature="sa{sv}")
    def IndexingFinished(self, uri: str, stats: dict) -> None:
        pass
