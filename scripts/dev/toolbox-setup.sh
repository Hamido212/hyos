#!/usr/bin/env bash
# hyos/scripts/dev/toolbox-setup.sh
#
# DEV ENVIRONMENT SETUP — run inside a Toolbx container
# -------------------------------------------------------
# Toolbx provides a mutable Fedora container on an Atomic host,
# allowing dnf install and pip without touching the immutable host.
#
# Usage:
#   toolbox create hyos-dev
#   toolbox enter hyos-dev
#   bash scripts/dev/toolbox-setup.sh
#
# Reference:
#   https://docs.fedoraproject.org/en-US/atomic-desktops/toolbox/

set -euo pipefail

HYOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> HyOS dev setup inside Toolbx"
echo "    Repo: $HYOS_ROOT"
echo ""

# --- Verify we're inside toolbox ---
if [[ ! -f /run/.toolboxenv ]]; then
    echo "ERROR: This script must run inside a Toolbx container."
    echo "       Create and enter one first:"
    echo "         toolbox create hyos-dev"
    echo "         toolbox enter hyos-dev"
    exit 1
fi

# --- Development dependencies ---
echo "==> Installing dev dependencies (dnf inside toolbox)..."
sudo dnf install -y \
    python3-dbus \
    python3-gobject \
    poppler-utils \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    dbus-tools \
    gcc \
    python3-devel

# --- Install HyOS Python packages in editable mode ---
echo ""
echo "==> Installing HyOS packages (editable)..."
pip install --user -e "$HYOS_ROOT/services/hyos-policyd"
pip install --user -e "$HYOS_ROOT/services/hyos-indexerd"
pip install --user -e "$HYOS_ROOT/services/hyos-docd"
pip install --user -e "$HYOS_ROOT/services/hyos-routerd"
pip install --user -e "$HYOS_ROOT/shell/gnome-search-provider"

echo ""
echo "==> Dev environment ready."
echo ""
echo "    You can now run services manually inside toolbox for testing:"
echo "      hyos-policyd &"
echo "      hyos-indexerd &"
echo "      hyos-docd &"
echo "      hyos-routerd &"
echo ""
echo "    Note: GNOME Shell search integration and systemd --user services"
echo "    run on the HOST, not inside toolbox. See scripts/dev/session-setup.sh"
