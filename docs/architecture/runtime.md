# Runtime Architecture

## Service lifecycle

All HyOS runtime services are **systemd user services** with D-Bus activation. They are not started at login unconditionally — they are started on demand when their D-Bus name is first requested, and may be stopped after a configurable idle timeout.

```
User session start
  └── systemd --user starts (already running)
        └── D-Bus session daemon starts

User opens GNOME Activities and types a search query
  → GNOME Shell calls GetInitialResultSet on hyos-search-provider
    → D-Bus activates hyos-search-provider (if not running)
      → hyos-search-provider calls org.hyos.Router1
        → D-Bus activates hyos-routerd (if not running)
          → hyos-routerd calls org.hyos.Indexer1
            → D-Bus activates hyos-indexerd (if not running)
```

This lazy activation model means HyOS has zero overhead when not in use.

## Service responsibilities

### hyos-routerd

The orchestrator. It is the single entry point for all task requests from the search provider and HyOS apps. No other component calls Ollama or `hyos-docd` directly.

Responsibilities:
- Accept `RunTask` calls from authorized callers
- Evaluate capability availability (`ListCapabilities`)
- Call `hyos-policyd` for authorization before executing any task
- Route tasks to the appropriate backend service
- Manage job lifecycle (create, update, cancel, finish)
- Emit `JobUpdated` and `JobFinished` signals for streaming UI updates
- Maintain a model adapter abstraction over Ollama

### hyos-indexerd

The local content indexer. Runs in the background after being activated, does not continuously poll the filesystem.

Responsibilities:
- Index allowed paths (`~/Documents`, `~/Downloads`, `~/Desktop`) on request
- Store metadata and text excerpts in `~/.local/share/hyos/index/`
- Answer `Search(query, limit)` calls with ranked results
- Answer `GetDocumentMeta(doc_id)` and `GetSnippet(doc_id, query)` calls
- Watch for file changes via inotify and update index incrementally

The indexer never calls Ollama. Semantic reranking is done by `hyos-routerd` on top of the indexer's lexical results.

### hyos-docd

The document workflow service. Stateless between calls.

Responsibilities:
- Extract plain text from documents (PDF, DOCX, ODT, TXT, HTML)
- Construct prompts for Summarize / ExtractDeadlines / Translate / DraftReply
- Call Ollama via localhost HTTP
- Return structured results over D-Bus

`hyos-docd` does not write any files. It returns data; the caller decides what to do with it.

### hyos-policyd

The policy engine. Very small and fast — every task request must go through it.

Responsibilities:
- Evaluate a proposed action against the current mode
- Return: `allow`, `deny`, or `require_confirmation`
- Report the current mode (`local-only`, `read-only`, `confirm-on-write`)
- Explain the last decision (for debugging and audit logs)

Policy modes in v0.1:

| Mode | What it means |
|---|---|
| `local-only` | No network requests. Ollama on localhost is allowed. No cloud. |
| `read-only` | No file writes. No mail sends. No shell execution. |
| `confirm-on-write` | (Future) Write actions require explicit user confirmation UI. |

v0.1 runs `local-only` + `read-only` by default. Both cannot be disabled through normal user flow in v0.1.

## IPC summary

```
hyos-search-provider
  → org.hyos.Router1    (RunTask, ListCapabilities)
  → org.hyos.Indexer1   (Search, GetDocumentMeta, GetSnippet)

hyos-routerd
  → org.hyos.Policy1    (Evaluate)
  → org.hyos.Documents1 (SummarizeUri, ExtractDeadlinesUri, ...)
  → Ollama HTTP         (localhost:11434/api/generate)

hyos-docd
  → Ollama HTTP         (localhost:11434/api/generate)

hyos-inspector (app)
  → org.hyos.Documents1 (all methods)
  → org.hyos.Indexer1   (GetDocumentMeta, GetSnippet)

hyos-writer (app)
  → org.hyos.Documents1 (ProcessText)
```

## State storage

| Service | State location | Format |
|---|---|---|
| `hyos-indexerd` | `~/.local/share/hyos/index/` | SQLite + custom |
| `hyos-policyd` | `~/.config/hyos/policy.conf` | TOML |
| `hyos-routerd` | In-memory job map only | — |
| `hyos-docd` | Stateless | — |
