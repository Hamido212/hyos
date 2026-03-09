#!/usr/bin/env bash
# Smoke test: verify all HyOS D-Bus services are responding
# Run this after `scripts/dev/setup.sh` and starting the services.
#
# Usage:
#   systemctl --user start hyos-policyd hyos-indexerd hyos-docd hyos-routerd
#   bash scripts/test/smoke.sh

set -euo pipefail

PASS=0
FAIL=0

check() {
    local label="$1"
    local cmd="$2"
    local expected="$3"

    result="$(eval "$cmd" 2>/dev/null || echo "ERROR")"
    if echo "$result" | grep -q "$expected"; then
        echo "  PASS  $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $label"
        echo "        Expected: $expected"
        echo "        Got:      $result"
        FAIL=$((FAIL + 1))
    fi
}

echo "==> HyOS smoke tests"
echo ""

echo "--- hyos-policyd (org.hyos.Policy1) ---"
check "GetMode returns local-only" \
    "busctl --user call org.hyos.Policy1 /org/hyos/Policy org.hyos.Policy1 GetMode" \
    "local-only"

check "Evaluate returns allow for safe task" \
    "busctl --user call org.hyos.Policy1 /org/hyos/Policy org.hyos.Policy1 Evaluate 'a{sv}' 2 'type' s 'summarize' 'write' b false" \
    "allow"

echo ""
echo "--- hyos-indexerd (org.hyos.Indexer1) ---"
check "Search returns array" \
    "busctl --user call org.hyos.Indexer1 /org/hyos/Indexer org.hyos.Indexer1 Search 'su' 'test' 5" \
    "a{sv}"

echo ""
echo "--- hyos-routerd (org.hyos.Router1) ---"
check "ListCapabilities returns task types" \
    "busctl --user call org.hyos.Router1 /org/hyos/Router org.hyos.Router1 ListCapabilities" \
    "summarize"

check "RunTask returns a job ID" \
    "busctl --user call org.hyos.Router1 /org/hyos/Router org.hyos.Router1 RunTask 'a{sv}' 3 'type' s 'semantic_search' 'query' s 'test' 'limit' u 5" \
    '^\s*s "'

echo ""
echo "--- hyos-search-provider (tech.hyos.SearchProvider) ---"
check "GetInitialResultSet returns array" \
    "busctl --user call tech.hyos.SearchProvider /tech/hyos/SearchProvider org.gnome.Shell.SearchProvider2 GetInitialResultSet 'as' 1 'letter'" \
    "as"

echo ""
if [[ $FAIL -eq 0 ]]; then
    echo "All $PASS tests passed."
else
    echo "$PASS passed, $FAIL failed."
    exit 1
fi
