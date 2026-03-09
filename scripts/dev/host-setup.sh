#!/usr/bin/env bash
# hyos/scripts/dev/host-setup.sh
#
# HOST SETUP for Fedora Atomic Desktop (Silverblue / Kinoite)
# -----------------------------------------------------------
# Run this ONCE on the Fedora Atomic host — not inside a toolbox.
# This script only touches host-level concerns:
#   - rpm-ostree package layering for things that MUST be on the host
#   - D-Bus service file deployment (host D-Bus, not user bus)
#   - systemd user unit deployment
#   - GNOME Search Provider registration
#
# For all Python/dev work, use:
#   scripts/dev/toolbox-setup.sh
#
# Reference:
#   https://docs.fedoraproject.org/en-US/atomic-desktops/
#   https://docs.fedoraproject.org/en-US/atomic-desktops/toolbox/

set -euo pipefail

HYOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> HyOS host setup (Fedora Atomic)"
echo "    Repo: $HYOS_ROOT"
echo ""

# --- Verify we are on an Atomic host ---
if ! command -v rpm-ostree &>/dev/null; then
    echo "WARNING: rpm-ostree not found."
    echo "         This script targets Fedora Atomic Desktop (Silverblue/Kinoite)."
    echo "         On a standard Fedora workstation, use: sudo dnf install poppler-utils"
    echo "         then run scripts/dev/toolbox-setup.sh inside a toolbox."
fi

# --- Host-level packages via rpm-ostree ---
# Only layer packages that must exist on the HOST (not in toolbox).
# For HyOS, that is:
#   - poppler-utils: pdftotext must be accessible by the session service
#     outside a container (the systemd user service runs on the host)
#
# python3-dbus and python3-gobject are needed by the services on the HOST.
# They are in Fedora RPM repos and safe to layer.
echo "==> Layering required host packages via rpm-ostree..."
echo "    (This stages a reboot — services won't work until after reboot)"
echo ""
rpm-ostree install --idempotent --allow-inactive \
    python3-dbus \
    python3-gobject \
    poppler-utils \
    python3-pip

echo ""
echo "    Packages staged. Reboot required before continuing:"
echo "    systemctl reboot"
echo ""
echo "    After reboot, run:"
echo "    bash scripts/dev/toolbox-setup.sh   (inside a toolbox, for dev/build)"
echo "    bash scripts/dev/session-setup.sh   (on the host, for service deployment)"
