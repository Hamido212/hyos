"""
hyos-routerd — D-Bus proxy clients for backend services

Each client wraps D-Bus calls to a backend service with:
- Graceful fallback if the service is not running
- Type coercion from dbus types to plain Python types
"""

import logging

import dbus

log = logging.getLogger(__name__)


def _unpack(val):
    """Recursively unpack dbus types to plain Python types."""
    if hasattr(val, "items"):
        return {str(k): _unpack(v) for k, v in val.items()}
    if isinstance(val, (list, dbus.Array)):
        return [_unpack(v) for v in val]
    if isinstance(val, dbus.Boolean):
        return bool(val)
    if isinstance(val, (dbus.Int16, dbus.Int32, dbus.Int64,
                        dbus.UInt16, dbus.UInt32, dbus.UInt64)):
        return int(val)
    if isinstance(val, dbus.Double):
        return float(val)
    if isinstance(val, dbus.String):
        return str(val)
    if hasattr(val, "unpack"):
        return _unpack(val.unpack())
    return val


class PolicyClient:
    """Client for org.hyos.Policy1."""

    _BUS_NAME = "org.hyos.Policy1"
    _OBJECT_PATH = "/org/hyos/Policy"
    _IFACE = "org.hyos.Policy1"

    def __init__(self, bus: dbus.SessionBus) -> None:
        self._bus = bus

    def _proxy(self):
        return self._bus.get_object(self._BUS_NAME, self._OBJECT_PATH)

    def evaluate(self, action: dict) -> dict:
        """
        Returns {"decision": "allow"|"deny"|"require_confirmation", "reason": str}.
        Falls back to {"decision": "allow"} if policyd is unavailable.
        """
        try:
            dbus_action = {k: dbus.Variant("b", v) if isinstance(v, bool) else dbus.Variant("s", str(v))
                           for k, v in action.items()}
            result = self._proxy().Evaluate(dbus_action, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException as e:
            log.warning("PolicyClient: policyd unavailable (%s), defaulting to allow", e)
            return {"decision": "allow", "reason": "policyd unavailable, fallback allow"}


class IndexerClient:
    """Client for org.hyos.Indexer1."""

    _BUS_NAME = "org.hyos.Indexer1"
    _OBJECT_PATH = "/org/hyos/Indexer"
    _IFACE = "org.hyos.Indexer1"

    def __init__(self, bus: dbus.SessionBus) -> None:
        self._bus = bus

    def _proxy(self):
        return self._bus.get_object(self._BUS_NAME, self._OBJECT_PATH)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        try:
            results = self._proxy().Search(query, dbus.UInt32(limit), dbus_interface=self._IFACE)
            return _unpack(results)
        except dbus.exceptions.DBusException as e:
            log.warning("IndexerClient: indexerd unavailable (%s)", e)
            return []

    def get_meta(self, doc_id: str) -> dict | None:
        try:
            result = self._proxy().GetDocumentMeta(doc_id, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException:
            return None

    def get_snippet(self, doc_id: str, query: str) -> str:
        try:
            return str(self._proxy().GetSnippet(doc_id, query, dbus_interface=self._IFACE))
        except dbus.exceptions.DBusException:
            return ""


class DocClient:
    """Client for org.hyos.Documents1."""

    _BUS_NAME = "org.hyos.Documents1"
    _OBJECT_PATH = "/org/hyos/Documents"
    _IFACE = "org.hyos.Documents1"

    def __init__(self, bus: dbus.SessionBus) -> None:
        self._bus = bus

    def _proxy(self):
        return self._bus.get_object(self._BUS_NAME, self._OBJECT_PATH)

    def summarize(self, uri: str) -> dict:
        try:
            result = self._proxy().SummarizeUri(uri, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException as e:
            return {"error": str(e), "summary": ""}

    def extract_deadlines(self, uri: str) -> dict:
        try:
            result = self._proxy().ExtractDeadlinesUri(uri, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException as e:
            return {"error": str(e), "deadlines_json": "[]"}

    def translate(self, uri: str, target_lang: str) -> dict:
        try:
            result = self._proxy().TranslateUri(uri, target_lang, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException as e:
            return {"error": str(e), "translation": ""}

    def draft_reply(self, uri: str, tone: str) -> dict:
        try:
            result = self._proxy().DraftReplyUri(uri, tone, dbus_interface=self._IFACE)
            return _unpack(result)
        except dbus.exceptions.DBusException as e:
            return {"error": str(e), "draft": ""}
