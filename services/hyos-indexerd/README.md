# hyos-indexerd

Local file content indexer for HyOS.

## Responsibility

- Indexes user documents in allowed paths: `~/Documents`, `~/Downloads`, `~/Desktop`.
- Stores document metadata and extracted plain text in `~/.local/share/hyos/index/`.
- Answers `Search(query, limit)` calls with ranked results.
- Answers `GetDocumentMeta(doc_id)` and `GetSnippet(doc_id, query)` calls.
- Watches indexed paths for changes via inotify and updates the index incrementally.

## D-Bus interface

`org.hyos.Indexer1` on `/org/hyos/Indexer` — see [`docs/dbus/org.hyos.Indexer1.xml`](../../docs/dbus/org.hyos.Indexer1.xml).

## Supported file types (v0.1)

- PDF (via text extraction library — no script execution)
- DOCX / ODT
- Plain text (TXT, MD)
- HTML (stripped)

## Security

- Runs as a user service. No root.
- `ReadOnlyPaths=~/Documents ~/Downloads ~/Desktop` — hard limit in systemd unit.
- `InaccessiblePaths` blocks access to `~/.ssh`, `~/.gnupg`, `~/.config/chromium`, `~/.mozilla`, `~/.local/share/keyrings`, `/etc`, `/root`.
- Calls with URIs outside allowed paths return `org.hyos.Error.AccessDenied`.
- Does not execute macros, scripts, or embedded content from documents.
- Does not call Ollama. Semantic reranking is the router's responsibility.

## Storage

| Path | Contents |
|---|---|
| `~/.local/share/hyos/index/docs.db` | SQLite index: document metadata + text excerpts |
| `~/.local/share/hyos/index/fts/` | Full-text search index |

Index format is internal and may change between HyOS versions.

## Implementation notes

- Use `inotify` (via `inotify-simple` or equivalent) for file change watching.
- Text extraction must be done in a sandbox or with memory-safe parsers.
- `doc_id` is a stable hash of the canonical file path (not content, to handle edits without re-ID).
