"""
hyos-search-provider — GNOME Shell Search Provider implementation

Implements org.gnome.Shell.SearchProvider2.
This is a thin adapter: no AI logic lives here. It translates GNOME's
search protocol into HyOS D-Bus calls and formats results for GNOME.

Result ID format:  {type}:{doc_id}
  type = "doc" | "action"
"""

import hashlib
import logging
import subprocess

import dbus
import dbus.service

log = logging.getLogger(__name__)

_IFACE = "org.gnome.Shell.SearchProvider2"

# D-Bus proxies for backend services (lazy-initialized)
_INDEXER_BUS  = "org.hyos.Indexer1"
_INDEXER_PATH = "/org/hyos/Indexer"
_INDEXER_IFACE = "org.hyos.Indexer1"


def _unpack(val):
    """Recursively unpack dbus types to plain Python types."""
    if hasattr(val, "items"):
        return {str(k): _unpack(v) for k, v in val.items()}
    if isinstance(val, (list, dbus.Array)):
        return [_unpack(v) for v in val]
    if hasattr(val, "unpack"):
        return _unpack(val.unpack())
    return str(val) if isinstance(val, dbus.String) else val


class SearchProvider(dbus.service.Object):

    def __init__(self, bus: dbus.SessionBus) -> None:
        name = dbus.service.BusName("tech.hyos.SearchProvider", bus)
        super().__init__(name, "/tech/hyos/SearchProvider")
        self._bus = bus
        self._result_cache: dict[str, dict] = {}  # result_id → metadata
        log.info("SearchProvider ready")

    # ------------------------------------------------------------------ #
    # Backend access                                                       #
    # ------------------------------------------------------------------ #

    def _search_indexer(self, query: str, limit: int = 15) -> list[dict]:
        try:
            proxy = self._bus.get_object(_INDEXER_BUS, _INDEXER_PATH)
            results = proxy.Search(query, dbus.UInt32(limit), dbus_interface=_INDEXER_IFACE)
            return _unpack(results)
        except dbus.exceptions.DBusException as e:
            log.debug("Indexer unavailable: %s", e)
            return []

    def _get_doc_meta(self, doc_id: str) -> dict | None:
        try:
            proxy = self._bus.get_object(_INDEXER_BUS, _INDEXER_PATH)
            result = proxy.GetDocumentMeta(doc_id, dbus_interface=_INDEXER_IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException:
            return None

    # ------------------------------------------------------------------ #
    # Result building                                                      #
    # ------------------------------------------------------------------ #

    def _build_results(self, query: str) -> list[str]:
        """
        Query backends and return a list of result IDs.
        Also populates self._result_cache.
        """
        result_ids = []
        index_results = self._search_indexer(query)

        for r in index_results:
            doc_id = str(r.get("doc_id", ""))
            if not doc_id:
                continue
            result_id = f"doc:{doc_id}"
            self._result_cache[result_id] = {
                "id":          result_id,
                "name":        str(r.get("name", "")),
                "description": str(r.get("snippet", "")) or str(r.get("uri", "")),
                "uri":         str(r.get("uri", "")),
                "mimetype":    str(r.get("mimetype", "")),
                "doc_id":      doc_id,
            }
            result_ids.append(result_id)

        # Add a contextual AI action if we found any documents
        if index_results:
            top_doc_id = str(index_results[0].get("doc_id", ""))
            if top_doc_id:
                action_id = f"action:analyze:{top_doc_id}"
                top_name  = str(index_results[0].get("name", "document"))
                self._result_cache[action_id] = {
                    "id":          action_id,
                    "name":        f"Analyze: {top_name}",
                    "description": "HyOS · Summarize, extract deadlines, draft reply",
                    "uri":         str(index_results[0].get("uri", "")),
                    "doc_id":      top_doc_id,
                    "is_action":   True,
                }
                result_ids.insert(0, action_id)  # Actions appear first

        return result_ids

    # ------------------------------------------------------------------ #
    # org.gnome.Shell.SearchProvider2 interface                           #
    # ------------------------------------------------------------------ #

    @dbus.service.method(
        dbus_interface=_IFACE,
        in_signature="as",
        out_signature="as",
    )
    def GetInitialResultSet(self, terms: list) -> list:
        query = " ".join(str(t) for t in terms)
        log.debug("GetInitialResultSet: %r", query)
        if len(query.strip()) < 2:
            return dbus.Array([], signature="s")
        result_ids = self._build_results(query)
        return dbus.Array(result_ids[:10], signature="s")

    @dbus.service.method(
        dbus_interface=_IFACE,
        in_signature="asas",
        out_signature="as",
    )
    def GetSubsearchResultSet(self, previous_results: list, terms: list) -> list:
        # Re-search with refined terms (GNOME calls this for incremental refinement)
        query = " ".join(str(t) for t in terms)
        log.debug("GetSubsearchResultSet: %r", query)
        if len(query.strip()) < 2:
            return dbus.Array([], signature="s")
        result_ids = self._build_results(query)
        # Intersect with previous_results if any, for performance
        prev_set = set(str(r) for r in previous_results)
        if prev_set:
            filtered = [r for r in result_ids if r in prev_set]
            if filtered:
                return dbus.Array(filtered[:10], signature="s")
        return dbus.Array(result_ids[:10], signature="s")

    @dbus.service.method(
        dbus_interface=_IFACE,
        in_signature="as",
        out_signature="aa{sv}",
    )
    def GetResultMetas(self, identifiers: list) -> list:
        metas = []
        for result_id in identifiers:
            result_id = str(result_id)
            cached = self._result_cache.get(result_id)
            if not cached:
                # Try to recover from cache miss (e.g. service restart)
                continue

            is_action = cached.get("is_action", False)
            gicon = "system-run-symbolic" if is_action else _mime_icon(cached.get("mimetype", ""))

            meta = dbus.Dictionary({
                "id":          dbus.String(result_id),
                "name":        dbus.String(cached.get("name", result_id)),
                "description": dbus.String(cached.get("description", "")),
                "gicon":       dbus.String(gicon),
            }, signature="sv")
            metas.append(meta)

        return dbus.Array(metas, signature="a{sv}")

    @dbus.service.method(
        dbus_interface=_IFACE,
        in_signature="sasu",
        out_signature="",
    )
    def ActivateResult(self, identifier: str, terms: list, timestamp: int) -> None:
        result_id = str(identifier)
        cached = self._result_cache.get(result_id, {})
        uri   = cached.get("uri", "")
        doc_id = cached.get("doc_id", "")
        is_action = cached.get("is_action", False)

        log.info("ActivateResult: %s uri=%s", result_id, uri)

        # Launch HyOS Inspector with the result
        cmd = ["hyos-inspector"]
        if doc_id:
            cmd += ["--result-id", result_id]
        if uri:
            cmd += ["--uri", uri]
        if is_action:
            cmd += ["--action", "analyze"]

        try:
            subprocess.Popen(
                cmd,
                start_new_session=True,
                close_fds=True,
            )
        except FileNotFoundError:
            # hyos-inspector not yet built — fall back to xdg-open for the file
            log.warning("hyos-inspector not found, falling back to xdg-open")
            if uri:
                try:
                    subprocess.Popen(["xdg-open", uri], start_new_session=True, close_fds=True)
                except Exception as e:
                    log.error("xdg-open failed: %s", e)

    @dbus.service.method(
        dbus_interface=_IFACE,
        in_signature="asu",
        out_signature="",
    )
    def LaunchSearch(self, terms: list, timestamp: int) -> None:
        # Open HyOS Inspector in search mode with the query
        query = " ".join(str(t) for t in terms)
        log.info("LaunchSearch: %r", query)
        try:
            subprocess.Popen(
                ["hyos-inspector", "--search", query],
                start_new_session=True,
                close_fds=True,
            )
        except FileNotFoundError:
            log.warning("hyos-inspector not found, LaunchSearch is a no-op")


def _mime_icon(mimetype: str) -> str:
    """Return an icon name for a MIME type."""
    if "pdf" in mimetype:
        return "application-pdf"
    if "word" in mimetype or "document" in mimetype:
        return "application-msword"
    if "text" in mimetype:
        return "text-x-generic"
    if "image" in mimetype:
        return "image-x-generic"
    return "text-x-generic"
