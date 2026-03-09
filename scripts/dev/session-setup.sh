#!/usr/bin/env bash
# hyos/scripts/dev/session-setup.sh
#
# HOST SESSION SETUP — deploys HyOS services to the current user session
# -----------------------------------------------------------------------
# Run this AFTER:
#   1. scripts/dev/host-setup.sh  (rpm-ostree + reboot)
#   2. pip install --user in toolbox or directly on the rebooted host
#
# This script is idempotent: safe to run multiple times.

set -euo pipefail

HYOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "==> HyOS session setup"
echo "    Repo: $HYOS_ROOT"

# --- Install HyOS packages to HOST Python --------------------------------
# Services must run on the host (not inside toolbox) to reach the session
# D-Bus, the user filesystem, and GNOME Shell.
echo ""
echo "==> Installing HyOS packages to host user Python..."
pip3 install --user -e "$HYOS_ROOT/services/hyos-policyd"
pip3 install --user -e "$HYOS_ROOT/services/hyos-indexerd"
pip3 install --user -e "$HYOS_ROOT/services/hyos-docd"
pip3 install --user -e "$HYOS_ROOT/services/hyos-routerd"
pip3 install --user -e "$HYOS_ROOT/shell/gnome-search-provider"

# --- D-Bus activation files ----------------------------------------------
DBUS_SERVICES_DIR="$HOME/.local/share/dbus-1/services"
mkdir -p "$DBUS_SERVICES_DIR"
echo ""
echo "==> Deploying D-Bus activation files → $DBUS_SERVICES_DIR"
cp "$HYOS_ROOT/packaging/dbus/"*.service "$DBUS_SERVICES_DIR/"
echo "    $(ls "$HYOS_ROOT/packaging/dbus/"*.service | wc -l) files deployed"

# --- systemd user units ---------------------------------------------------
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_USER_DIR"
echo ""
echo "==> Deploying systemd user units → $SYSTEMD_USER_DIR"
cp "$HYOS_ROOT/packaging/systemd/user/"*.service "$SYSTEMD_USER_DIR/"
echo "    $(ls "$HYOS_ROOT/packaging/systemd/user/"*.service | wc -l) units deployed"
systemctl --user daemon-reload

# --- GNOME Search Provider registration -----------------------------------
GNOME_SP_DIR="$HOME/.local/share/gnome-shell/search-providers"
mkdir -p "$GNOME_SP_DIR"
echo ""
echo "==> Registering GNOME Search Provider → $GNOME_SP_DIR"
cp "$HYOS_ROOT/shell/gnome-search-provider/tech.hyos.SearchProvider.ini" "$GNOME_SP_DIR/"

APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
cp "$HYOS_ROOT/shell/gnome-search-provider/tech.hyos.SearchProvider.desktop" "$APPS_DIR/"
update-desktop-database "$APPS_DIR" 2>/dev/null || true

# --- Enable+start services -----------------------------------------------
echo ""
echo "==> Enabling and starting HyOS services..."
SERVICES=(
    hyos-policyd.service
    hyos-indexerd.service
    hyos-docd.service
    hyos-routerd.service
    hyos-search-provider.service
)
for svc in "${SERVICES[@]}"; do
    systemctl --user enable --now "$svc" && echo "    ✓ $svc" || echo "    ✗ $svc (check: journalctl --user -u $svc)"
done

echo ""
echo "==> Session setup complete."
echo ""
echo "    Status overview:"
systemctl --user status "${SERVICES[@]}" --no-pager -l 2>&1 | grep -E "Loaded:|Active:|●" || true
echo ""
echo "    Run smoke test:"
echo "      bash $HYOS_ROOT/scripts/test/smoke.sh"
