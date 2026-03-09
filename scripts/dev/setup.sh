#!/usr/bin/env bash
# HyOS developer setup script
# Run this on a Fedora Atomic Desktop (Silverblue) development machine.
# This script does NOT modify the base OS image.
# It installs development dependencies into the user environment.

set -euo pipefail

HYOS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> HyOS developer setup"
echo "    Repo: $HYOS_ROOT"
echo ""

# --- Verify base system ---
if ! command -v rpm-ostree &>/dev/null; then
    echo "WARNING: rpm-ostree not found. This script is designed for Fedora Atomic Desktop."
    echo "         Continuing anyway, but some steps may fail."
fi

# --- Check Ollama ---
echo "==> Checking Ollama..."
if ! command -v ollama &>/dev/null; then
    echo "    Ollama not found."
    echo "    Install with: curl -fsSL https://ollama.com/install.sh | sh"
    echo "    Then enable: systemctl --user enable --now ollama"
    echo "    Then pull a model: ollama pull mistral"
    exit 1
fi

if ! systemctl --user is-active ollama &>/dev/null; then
    echo "    Ollama is not running. Starting..."
    systemctl --user enable --now ollama
fi

if ! curl -sf http://127.0.0.1:11434/api/version &>/dev/null; then
    echo "ERROR: Ollama API not reachable at localhost:11434"
    exit 1
fi
echo "    Ollama OK"

# --- Check D-Bus tools ---
echo "==> Checking D-Bus tools..."
for tool in busctl gdbus dbus-send; do
    if ! command -v "$tool" &>/dev/null; then
        echo "WARNING: $tool not found. Install glib2-devel package."
    fi
done

# --- Create runtime directories ---
echo "==> Checking Python D-Bus dependencies..."
python3 -c "import dbus" 2>/dev/null || {
    echo "    python3-dbus not found. Installing..."
    sudo dnf install -y python3-dbus python3-gobject poppler-utils
}

echo "==> Creating HyOS runtime directories..."
mkdir -p "$HOME/.local/share/hyos/index"
mkdir -p "$HOME/.local/share/hyos/policy"
mkdir -p "$HOME/.config/hyos"

# --- Install default policy config if not present ---
POLICY_CONF="$HOME/.config/hyos/policy.conf"
if [[ ! -f "$POLICY_CONF" ]]; then
    echo "==> Writing default policy config..."
    cat > "$POLICY_CONF" << 'EOF'
[policy]
mode = "local-only"
allow_localhost_network = true
allow_writes = false
allow_shell_execution = false
allow_privileged = false
EOF
fi

# --- Install systemd user units (symlinks for development) ---
echo "==> Installing systemd user units (dev symlinks)..."
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_USER_DIR"

for unit in "$HYOS_ROOT/packaging/systemd/user/"*.service; do
    name="$(basename "$unit")"
    target="$SYSTEMD_USER_DIR/$name"
    if [[ ! -L "$target" ]]; then
        ln -sf "$unit" "$target"
        echo "    Linked $name"
    fi
done

systemctl --user daemon-reload

# --- Install Python packages in editable/dev mode ---
echo "==> Installing HyOS Python packages (editable mode)..."
pip install --user -e "$HYOS_ROOT/services/hyos-policyd"
pip install --user -e "$HYOS_ROOT/services/hyos-indexerd"
pip install --user -e "$HYOS_ROOT/services/hyos-docd"
pip install --user -e "$HYOS_ROOT/services/hyos-routerd"
pip install --user -e "$HYOS_ROOT/shell/gnome-search-provider"

# --- Install D-Bus activation files for session bus ---
echo "==> Installing D-Bus session service files..."
DBUS_SERVICE_DIR="$HOME/.local/share/dbus-1/services"
mkdir -p "$DBUS_SERVICE_DIR"

for svc in "$HYOS_ROOT/packaging/dbus/"*.service; do
    name="$(basename "$svc")"
    target="$DBUS_SERVICE_DIR/$name"
    # Rewrite Exec= to use the pip-installed entry point
    binary="$(basename "$svc" .service | tr '.' '-' | tr '[:upper:]' '[:lower:]')"
    sed "s|Exec=.*|Exec=$(which "$binary" 2>/dev/null || echo "/usr/libexec/hyos/$binary")|" \
        "$svc" > "$target"
    echo "    Installed $name"
done

echo ""
echo "==> Setup complete."
echo ""
echo "    To verify the D-Bus environment once services are built:"
echo "    busctl --user list | grep hyos"
echo ""
echo "    To check a service hardening score (once running):"
echo "    systemd-analyze security --user hyos-routerd.service"
echo ""
echo "    To pull a default model (if not done yet):"
echo "    ollama pull mistral"
