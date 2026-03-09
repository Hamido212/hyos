"""
hyos-docd — D-Bus service implementation (org.hyos.Documents1)

All methods are read-only with respect to the filesystem.
They extract text, call Ollama, and return data — nothing is written.
"""

import json
import logging
import time

import dbus
import dbus.service

from . import extractor, ollama

log = logging.getLogger(__name__)


def _sv(val):
    if isinstance(val, bool):
        return dbus.Boolean(val)
    if isinstance(val, int):
        return dbus.Int64(val)
    if isinstance(val, float):
        return dbus.Double(val)
    return dbus.String(str(val) if val is not None else "")


def _timed(fn):
    """Call fn() and return (result, elapsed_seconds)."""
    t0 = time.monotonic()
    result = fn()
    return result, time.monotonic() - t0


class DocumentService(dbus.service.Object):

    def __init__(self, bus: dbus.SessionBus) -> None:
        name = dbus.service.BusName("org.hyos.Documents1", bus)
        super().__init__(name, "/org/hyos/Documents")
        log.info("DocumentService ready")

    # ------------------------------------------------------------------ #
    # D-Bus interface: org.hyos.Documents1                                #
    # ------------------------------------------------------------------ #

    @dbus.service.method(
        dbus_interface="org.hyos.Documents1",
        in_signature="s",
        out_signature="a{sv}",
    )
    def SummarizeUri(self, uri: str) -> dict:
        log.info("SummarizeUri: %s", uri)
        try:
            text = extractor.extract_text(str(uri))
            if not text.strip():
                return dbus.Dictionary({"summary": _sv(""), "error": _sv("No text could be extracted from this document.")}, signature="sv")
            summary, elapsed = _timed(lambda: ollama.summarize(text))
            return dbus.Dictionary({
                "summary":  _sv(summary),
                "language": _sv(""),
                "model":    _sv(ollama._get_model()),
                "duration": dbus.Double(round(elapsed, 2)),
            }, signature="sv")
        except PermissionError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.AccessDenied", str(e))
        except RuntimeError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.ModelUnavailable", str(e))
        except Exception as e:
            log.exception("SummarizeUri failed")
            raise dbus.exceptions.DBusException("org.hyos.Error.InternalError", str(e))

    @dbus.service.method(
        dbus_interface="org.hyos.Documents1",
        in_signature="s",
        out_signature="a{sv}",
    )
    def ExtractDeadlinesUri(self, uri: str) -> dict:
        log.info("ExtractDeadlinesUri: %s", uri)
        try:
            text = extractor.extract_text(str(uri))
            raw, elapsed = _timed(lambda: ollama.extract_deadlines(text))
            # Parse JSON output; fall back to raw string on failure
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    parsed = []
            except json.JSONDecodeError:
                parsed = []
            deadlines_str = json.dumps(parsed)
            return dbus.Dictionary({
                "deadlines_json": _sv(deadlines_str),
                "model":          _sv(ollama._get_model()),
                "language":       _sv(""),
                "duration":       dbus.Double(round(elapsed, 2)),
            }, signature="sv")
        except PermissionError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.AccessDenied", str(e))
        except RuntimeError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.ModelUnavailable", str(e))
        except Exception as e:
            log.exception("ExtractDeadlinesUri failed")
            raise dbus.exceptions.DBusException("org.hyos.Error.InternalError", str(e))

    @dbus.service.method(
        dbus_interface="org.hyos.Documents1",
        in_signature="ss",
        out_signature="a{sv}",
    )
    def TranslateUri(self, uri: str, target_lang: str) -> dict:
        log.info("TranslateUri: %s → %s", uri, target_lang)
        try:
            text = extractor.extract_text(str(uri))
            translation, elapsed = _timed(lambda: ollama.translate(text, str(target_lang)))
            return dbus.Dictionary({
                "translation": _sv(translation),
                "source_lang": _sv(""),
                "model":       _sv(ollama._get_model()),
                "duration":    dbus.Double(round(elapsed, 2)),
            }, signature="sv")
        except PermissionError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.AccessDenied", str(e))
        except RuntimeError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.ModelUnavailable", str(e))
        except Exception as e:
            log.exception("TranslateUri failed")
            raise dbus.exceptions.DBusException("org.hyos.Error.InternalError", str(e))

    @dbus.service.method(
        dbus_interface="org.hyos.Documents1",
        in_signature="ss",
        out_signature="a{sv}",
    )
    def DraftReplyUri(self, uri: str, tone: str) -> dict:
        log.info("DraftReplyUri: %s tone=%s", uri, tone)
        try:
            text = extractor.extract_text(str(uri))
            draft, elapsed = _timed(lambda: ollama.draft_reply(text, str(tone)))
            return dbus.Dictionary({
                "draft":    _sv(draft),
                "language": _sv(""),
                "model":    _sv(ollama._get_model()),
                "duration": dbus.Double(round(elapsed, 2)),
            }, signature="sv")
        except PermissionError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.AccessDenied", str(e))
        except RuntimeError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.ModelUnavailable", str(e))
        except Exception as e:
            log.exception("DraftReplyUri failed")
            raise dbus.exceptions.DBusException("org.hyos.Error.InternalError", str(e))

    @dbus.service.method(
        dbus_interface="org.hyos.Documents1",
        in_signature="ssa{sv}",
        out_signature="a{sv}",
    )
    def ProcessText(self, action: str, text: str, options: dict) -> dict:
        log.info("ProcessText action=%s text_len=%d", action, len(str(text)))
        try:
            py_options = {str(k): str(v) for k, v in options.items()}
            output, elapsed = _timed(
                lambda: ollama.process_text(str(action), str(text), py_options)
            )
            return dbus.Dictionary({
                "output":   _sv(output),
                "model":    _sv(ollama._get_model()),
                "action":   _sv(str(action)),
                "duration": dbus.Double(round(elapsed, 2)),
            }, signature="sv")
        except ValueError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.InvalidArgument", str(e))
        except RuntimeError as e:
            raise dbus.exceptions.DBusException("org.hyos.Error.ModelUnavailable", str(e))
        except Exception as e:
            log.exception("ProcessText failed")
            raise dbus.exceptions.DBusException("org.hyos.Error.InternalError", str(e))
