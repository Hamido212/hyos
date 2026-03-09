# Vertical Slice Test Plan — HyOS v0.1

**Scope**: The single path that proves the project works:  
`PDF exists on disk → indexed → searchable → analyzed by local AI → GNOME sees the result`

**Target environment**: Fedora Atomic Desktop (Silverblue), GNOME Shell ≥ 45, Ollama with `mistral` model, session-setup.sh already executed.

---

## Prerequisites checklist

Run these before starting. Every item must pass.

```bash
# 1. All five HyOS services are running
systemctl --user is-active hyos-policyd hyos-indexerd hyos-docd hyos-routerd hyos-search-provider

# Expected output (one per line):
# active
# active
# active
# active
# active
```

```bash
# 2. Ollama is available and the model is present
curl -s http://127.0.0.1:11434/api/version | python3 -m json.tool
ollama list | grep mistral
```

```bash
# 3. D-Bus activation is registered
busctl --user list | grep hyos
# Expected: org.hyos.Router1 org.hyos.Indexer1 org.hyos.Documents1 org.hyos.Policy1 tech.hyos.SearchProvider
```

If any item fails, stop. Diagnose with `journalctl --user -u <service-name> -n 50 --no-pager` before continuing.

---

## Step 1 — Place the test document

```bash
# Use any real PDF. A letter or project brief works best for deadline extraction.
cp /path/to/your/document.pdf ~/Downloads/hyos-test.pdf

# Verify it exists and is readable
ls -lh ~/Downloads/hyos-test.pdf
pdftotext ~/Downloads/hyos-test.pdf - | head -20
```

**Expected**: 20 lines of readable text. If `pdftotext` returns nothing, the PDF is image-only — use a text-based PDF.

---

## Step 2 — Index the document

```bash
busctl --user call \
    org.hyos.Indexer1 /org/hyos/Indexer \
    org.hyos.Indexer1 IndexPath "sb" \
    "file://$HOME/Downloads/hyos-test.pdf" false
```

**Expected output**:
```
b true
```

**If** `b false` is returned, check indexer logs:
```bash
journalctl --user -u hyos-indexerd -n 30 --no-pager
```

Common failure causes:
- `pdftotext` not installed on host (run `which pdftotext`; re-run `host-setup.sh` if missing)
- Path not inside `~/Documents`, `~/Downloads`, or `~/Desktop` — the indexer rejects other roots

---

## Step 3 — Verify the document is in the index

```bash
# Use a word you can see in the first 20 lines from Step 1
busctl --user call \
    org.hyos.Indexer1 /org/hyos/Indexer \
    org.hyos.Indexer1 Search "su" \
    "test" 5
```

**Expected**: A D-Bus array containing at least one result dict with `uri`, `name`, `score`, and `snippet` keys. The snippet should contain text from your PDF.

**If** the result is empty: the FTS5 index may not have committed yet. Wait 2 seconds and retry. If still empty, check `~/.local/share/hyos/index.db`:
```bash
sqlite3 ~/.local/share/hyos/index.db "SELECT path, mtime FROM docs;"
```

---

## Step 4 — Get document metadata

```bash
# Retrieve the doc_id from the Search result above, then:
DOC_URI="file://$HOME/Downloads/hyos-test.pdf"
busctl --user call \
    org.hyos.Indexer1 /org/hyos/Indexer \
    org.hyos.Indexer1 GetDocumentMeta "s" \
    "$DOC_URI"
```

**Expected**: A dict with `doc_id`, `uri`, `name`, `mimetype`, `mtime`, `size`.

---

## Step 5 — Summarize with local AI

```bash
DOC_URI="file://$HOME/Downloads/hyos-test.pdf"
busctl --user call \
    org.hyos.Documents1 /org/hyos/Documents \
    org.hyos.Documents1 SummarizeUri "s" \
    "$DOC_URI"
```

**Expected**: A D-Bus dict with a `summary` key containing a readable paragraph from Ollama. Time is typically 5–30 seconds depending on hardware.

**Failure modes:**
- `org.hyos.Error.ModelUnavailable` → Ollama is not running (`systemctl --user start ollama`)
- `org.hyos.Error.AccessDenied` → path is outside allowed roots (check the URI)
- `org.hyos.Error.InternalError` → check docd logs: `journalctl --user -u hyos-docd -n 50 --no-pager`

---

## Step 6 — Extract deadlines

```bash
DOC_URI="file://$HOME/Downloads/hyos-test.pdf"
busctl --user call \
    org.hyos.Documents1 /org/hyos/Documents \
    org.hyos.Documents1 ExtractDeadlinesUri "s" \
    "$DOC_URI"
```

**Expected**: A dict with `deadlines` key containing a JSON array of deadline objects. If the document has no dates, an empty array `[]` is valid — the service must not error on a document without dates.

---

## Step 7 — Policy gate (write action must be blocked)

This confirms the policy service is enforcing the v0.1 "local-only / no-write" rule.

```bash
busctl --user call \
    org.hyos.Policy1 /org/hyos/Policy \
    org.hyos.Policy1 Evaluate "a{sv}" 2 \
    "action" s "write_file" \
    "write" b true
```

**Expected**:
```
a{sv} 2 "decision" s "deny" "reason" s "..."
```

`"decision" "deny"` is the correct result. If `"allow"` is returned, the policy service is misconfigured — stop and fix before proceeding.

---

## Step 8 — Router orchestration

Confirm the router correctly proxies a semantic search through the policy gate to the indexer.

```bash
busctl --user call \
    org.hyos.Router1 /org/hyos/Router \
    org.hyos.Router1 RunTask "a{sv}" 2 \
    "task_type" s "semantic_search" \
    "query" s "test"
```

**Expected**: A D-Bus struct with a `job_id` string.

Then poll the job:
```bash
JOB_ID="<job_id from above>"
busctl --user call \
    org.hyos.Router1 /org/hyos/Router \
    org.hyos.Router1 GetJob "s" "$JOB_ID"
```

**Expected**: A dict with `state: "finished"` and a `result` key containing search hits. (Jobs run in a background thread — poll a second time if state is still `"running"`.)

---

## Step 9 — GNOME Shell search integration

This is the first real "magical moment" test. No `busctl` — real GNOME UI.

1. Press the **Super** key to open the Activities overview.
2. Type a word that appears in your test PDF.
3. Wait up to 3 seconds.

**Expected**: A result group labelled "HyOS" appears below the file manager results, containing the PDF with a snippet. Clicking the result opens the file with `xdg-open` (or `hyos-inspector` if installed).

**If no HyOS group appears:**

```bash
# Check the search provider is registered
ls ~/.local/share/gnome-shell/search-providers/
# Expected: tech.hyos.SearchProvider.ini

# Check the provider is active
busctl --user list | grep tech.hyos.SearchProvider

# Check GNOME search settings — provider may be disabled
gsettings get org.gnome.desktop.search-providers disabled
# If tech.hyos.SearchProvider is in the list, remove it:
gsettings set org.gnome.desktop.search-providers disabled "[]"

# Check provider logs
journalctl --user -u hyos-search-provider -n 50 --no-pager
```

---

## Step 10 — End-to-end via Router (summarize task)

Confirm the router can orchestrate a full AI document workflow.

```bash
DOC_URI="file://$HOME/Downloads/hyos-test.pdf"
busctl --user call \
    org.hyos.Router1 /org/hyos/Router \
    org.hyos.Router1 RunTask "a{sv}" 2 \
    "task_type" s "summarize" \
    "uri" s "$DOC_URI"
```

Poll with `GetJob` until `state: "finished"`. The `result` dict should contain a `summary` field.

---

## Pass criteria

The vertical slice is validated when ALL of the following are true:

| # | Check | Result |
|---|-------|--------|
| 1 | All 5 services active | `systemctl --user is-active` = `active` ×5 |
| 2 | IndexPath returns `true` | `b true` |
| 3 | Search returns ≥1 result for a word in the PDF | Array with ≥1 entry |
| 4 | SummarizeUri returns readable text | `summary` key present, non-empty |
| 5 | Write action returns `deny` | `decision = deny` from Policy1 |
| 6 | Router.GetJob state = `finished` for search | `state = finished`, results present |
| 7 | GNOME Activities search shows HyOS group | Group visible in GNOME Shell UI |

---

## Known limitations (v0.1)

- Image-only PDFs are not indexed (no OCR support)
- Ollama must be pre-started; auto-start via systemd user socket is not wired yet
- `hyos-inspector` is not yet built; `ActivateResult` falls back to `xdg-open`
- GNOME search provider result icons use generic MIME icons; doc-type icons not yet customized
- SELinux is in permissive mode; policy modules are not yet written

---

## Failure reference

| Error | Cause | Fix |
|---|---|---|
| Service not found on bus | Service not started | `systemctl --user start <service>` |
| `AccessDenied` from Indexer/Doc | Path outside allowed roots | Use `~/Documents`, `~/Downloads`, or `~/Desktop` |
| `ModelUnavailable` from docd | Ollama not running | `systemctl --user start ollama` |
| Empty FTS5 search result | Index not yet committed | Wait 2s, retry; check `index.db` |
| No HyOS group in GNOME | Provider disabled or not registered | Check `gsettings` + `.ini` file + provider logs |
| `pdftotext` missing | Host setup incomplete | Re-run `host-setup.sh` + reboot |
