"""
hyos-policyd — HyOS policy engine

Evaluates whether a proposed task is permitted under the current
policy mode. Called by hyos-routerd before every task execution.

v0.0.1 — always enforces local-only + read-only.
"""

import logging
import os
import tomllib
from pathlib import Path

import dbus
import dbus.service

log = logging.getLogger(__name__)

# Path to user policy config
_CONFIG_PATH = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "hyos" / "policy.conf"

_DEFAULT_CONFIG = {
    "policy": {
        "mode": "local-only",
        "allow_localhost_network": True,
        "allow_writes": False,
        "allow_shell_execution": False,
        "allow_privileged": False,
    }
}


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        try:
            with open(_CONFIG_PATH, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            log.warning("Failed to load policy config, using defaults: %s", e)
    return _DEFAULT_CONFIG


def _sv(val):
    """Wrap a plain Python value in the appropriate dbus-python typed object.

    dbus.Variant was removed in dbus-python 1.4. For a{sv} dicts we instead
    use concrete dbus types directly; dbus-python infers the variant signature
    from the type of the object.
    """
    if isinstance(val, bool):
        return dbus.Boolean(val)
    if isinstance(val, int):
        return dbus.Int64(val)
    if isinstance(val, float):
        return dbus.Double(val)
    return dbus.String(str(val))


class PolicyService(dbus.service.Object):

    def __init__(self, bus: dbus.SessionBus):
        name = dbus.service.BusName("org.hyos.Policy1", bus)
        super().__init__(name, "/org/hyos/Policy")
        self._config = _load_config()
        self._last_decision: dict[str, str] = {}  # caller_unique_name → explanation
        log.info("PolicyService ready (mode=%s)", self._get_mode())

    def _get_mode(self) -> str:
        return self._config.get("policy", {}).get("mode", "local-only")

    def _evaluate(self, action: dict) -> tuple[str, str]:
        """
        Returns (decision, reason).
        decision: "allow" | "deny" | "require_confirmation"
        """
        mode = self._get_mode()
        pol = self._config.get("policy", {})

        # Network check — only localhost is allowed
        if action.get("network", False):
            target = str(action.get("network_target", ""))
            if target not in ("localhost", "127.0.0.1", "::1", ""):
                return "deny", f"External network access denied in mode '{mode}'"

        # Write check
        if action.get("write", False) and not pol.get("allow_writes", False):
            return "deny", f"Write actions denied in mode '{mode}'"

        # Shell execution check
        if action.get("shell", False) and not pol.get("allow_shell_execution", False):
            return "deny", f"Shell execution denied in mode '{mode}'"

        # Privileged check
        if action.get("privileged", False) and not pol.get("allow_privileged", False):
            return "deny", f"Privileged actions denied in mode '{mode}'"

        return "allow", f"Permitted under mode '{mode}'"

    # ------------------------------------------------------------------ #
    # D-Bus interface: org.hyos.Policy1                                   #
    # ------------------------------------------------------------------ #

    @dbus.service.method(
        dbus_interface="org.hyos.Policy1",
        in_signature="a{sv}",
        out_signature="a{sv}",
        sender_keyword="sender",
    )
    def Evaluate(self, action: dict, sender: str = "") -> dict:
        py_action = {str(k): v.unpack() if hasattr(v, "unpack") else v for k, v in action.items()}
        decision, reason = self._evaluate(py_action)
        explanation = f"{decision.upper()}: {reason}"
        if sender:
            self._last_decision[sender] = explanation
        log.debug("Evaluate caller=%s action=%s → %s", sender, py_action.get("type", "?"), decision)
        if decision == "deny":
            log.info("DENY action=%s reason=%s", py_action.get("type", "?"), reason)
        return dbus.Dictionary(
            {
                "decision": _sv(decision),
                "reason": _sv(reason),
                "policy_mode": _sv(self._get_mode()),
            },
            signature="sv",
        )

    @dbus.service.method(
        dbus_interface="org.hyos.Policy1",
        in_signature="",
        out_signature="s",
    )
    def GetMode(self) -> str:
        return self._get_mode()

    @dbus.service.method(
        dbus_interface="org.hyos.Policy1",
        in_signature="s",
        out_signature="",
    )
    def SetMode(self, mode: str) -> None:
        # v0.0.1: only local-only is supported; any attempt to enable
        # network/write modes is rejected.
        if mode != "local-only":
            raise dbus.exceptions.DBusException(
                "org.hyos.Error.NotImplemented",
                f"Mode '{mode}' cannot be set in v0.0.1",
            )
        log.info("SetMode called with '%s' (no change in v0.0.1)", mode)

    @dbus.service.method(
        dbus_interface="org.hyos.Policy1",
        in_signature="",
        out_signature="s",
        sender_keyword="sender",
    )
    def ExplainLastDecision(self, sender: str = "") -> str:
        return self._last_decision.get(sender, "No decision recorded for this caller.")

    # Signal: ModeChanged (emitted on future SetMode implementation)
    @dbus.service.signal(dbus_interface="org.hyos.Policy1", signature="ss")
    def ModeChanged(self, old_mode: str, new_mode: str) -> None:
        pass
