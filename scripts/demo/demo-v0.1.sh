#!/usr/bin/env bash
# HyOS v0.1 demo flow script
# Demonstrates the target end-to-end experience described in the v0.1 milestone.
# NOTE: This is a documentation script — it shows the intended commands,
#       not all of which will work until the services are implemented.

set -euo pipefail

echo "==> HyOS v0.1 Demo Flow"
echo "    GNOME Search → HyOS Result → Analyze Letter → Extract Deadline → Draft Reply"
echo ""

# Step 1: Verify services are running
echo "--- Step 1: Verify HyOS services ---"
busctl --user list | grep -E "hyos|SearchProvider" || true

# Step 2: List router capabilities
echo ""
echo "--- Step 2: Router capabilities ---"
busctl --user call org.hyos.Router1 /org/hyos/Router \
    org.hyos.Router1 ListCapabilities

# Step 3: Search via D-Bus (simulating what GNOME Shell does)
echo ""
echo "--- Step 3: Search for 'last letter' via Indexer ---"
busctl --user call org.hyos.Indexer1 /org/hyos/Indexer \
    org.hyos.Indexer1 Search "ss" "last letter" 5

# Step 4: Check policy mode
echo ""
echo "--- Step 4: Policy mode ---"
busctl --user call org.hyos.Policy1 /org/hyos/Policy \
    org.hyos.Policy1 GetMode

# Step 5: Summarize a document (replace path with a real PDF)
echo ""
echo "--- Step 5: Summarize a document ---"
echo "    (Replace the URI below with a real document path)"
busctl --user call org.hyos.Documents1 /org/hyos/Documents \
    org.hyos.Documents1 SummarizeUri "s" "file://$HOME/Downloads/example.pdf"

echo ""
echo "==> Demo complete. Open HyOS Inspector for the full UI experience."
