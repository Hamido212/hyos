# Architecture Overview

## Summary

HyOS is a Linux-native AI shell layer. It does not replace the kernel, window manager, or display server. It integrates AI capabilities into the standard GNOME desktop surface via well-defined extension points: GNOME Search Providers, D-Bus services, and XDG Desktop Portals.

The base system is **Fedora Atomic Desktop (Silverblue)**. This is non-negotiable for v0.x because:

- Image-based updates give reproducible system states.
- Rollback means AI-related system packages can be reverted if they break something.
- The read-only system layer (`/usr`) discourages ad-hoc mutations and forces proper packaging.
- SELinux is active and enforcing by default on Fedora, giving a real MAC layer.

## Layers

### 1. Base layer

| Component | Role |
|---|---|
| Fedora Atomic Desktop | OS base, image-based, rollback |
| GNOME | Desktop environment and shell surface |
| Wayland | Display protocol (Compositor is the authority) |
| systemd | Service manager, socket activation, security namespaces |
| SELinux | Mandatory access control |

HyOS does not fight any of these. It works with their extension points.

### 2. Session layer

Everything the user directly interacts with that is HyOS-specific.

| Component | Role |
|---|---|
| `hyos-search-provider` | GNOME Shell search integration via `org.gnome.Shell.SearchProvider2` |
| `hyos-inspector` app | GTK/libadwaita document result viewer |
| `hyos-writer` app | AI-integrated text editing |
| Desktop files | `.desktop` entries for HyOS apps/actions |

The Search Provider is the primary integration point for v0.1. GNOME routes search queries to all registered providers on the Session Bus. The provider returns result IDs, titles, descriptions, icons, and handles `ActivateResult` to open HyOS Inspector.

### 3. Runtime layer (Session Bus services)

All services are **user-scoped systemd services** on the **Session Bus**. They do not require or request root. They are activated by D-Bus name (socket activation pattern) and may be stopped when idle.

| Service | D-Bus name | Role |
|---|---|---|
| `hyos-routerd` | `org.hyos.Router1` | Task orchestrator, capability registry, job lifecycle |
| `hyos-indexerd` | `org.hyos.Indexer1` | Local file content indexer, semantic search |
| `hyos-docd` | `org.hyos.Documents1` | Document analysis workflows |
| `hyos-policyd` | `org.hyos.Policy1` | Policy decisions, mode management |

Services do not call each other's binaries. All IPC is D-Bus.

### 4. Model layer

| Component | Role |
|---|---|
| Ollama | Local model service (HTTP, localhost:11434) |

Ollama runs as a separate systemd user service. HyOS services call it via its local HTTP API. In v0.1, no other model backend is supported. The abstraction is hidden inside `hyos-routerd`'s model-adapter module, so future backends (local llama.cpp, cloud fallback) can be added without changing other services.

Ollama is accessed only from `hyos-routerd` and `hyos-docd`. No other service calls the model directly.

### 5. Security layer

Not a separate process — applied across all layers.

| Mechanism | Where applied |
|---|---|
| systemd user units | All runtime services |
| systemd hardening directives | All runtime services (see security.md) |
| SELinux labels | All HyOS processes and file paths |
| polkit | `hyos-privileged-helperd` (System Bus only, stub in v0.1) |
| XDG Desktop Portals | File access, clipboard, future UI permission flows |

## Data flows

### Search flow (v0.1)

```
User types in GNOME Activities search
  → GNOME Shell calls GetInitialResultSet(["query", "terms"])
    → hyos-search-provider receives
      → calls org.hyos.Indexer1.Search("query terms", limit=10)
        → hyos-indexerd returns matching doc IDs + metadata
      → calls org.hyos.Router1.RunTask({type: "semantic_search", query: ...})
        → hyos-routerd: policy check → call Ollama → return ranked results
    → hyos-search-provider returns result IDs to GNOME
  → GNOME calls GetResultMetas([id1, id2, ...])
    → hyos-search-provider returns {id, name, description, gicon} for each
  → User activates a result
    → GNOME calls ActivateResult(id, terms, timestamp)
      → hyos-search-provider launches hyos-inspector with result ID
```

### Document analysis flow (v0.1)

```
User opens hyos-inspector or selects "Analyze with HyOS" from context menu
  → hyos-inspector calls org.hyos.Documents1.SummarizeUri(uri)
    → hyos-docd: policy check (read-only path? freigegebener Pfad?)
    → hyos-docd: extract text from document (local, no model)
    → hyos-docd: call Ollama /api/generate with prompt + text
    → hyos-docd: return structured result {summary, deadlines, ...}
  → hyos-inspector renders result
  → User clicks "Draft Reply"
    → hyos-inspector calls org.hyos.Documents1.DraftReplyUri(uri, tone)
      → hyos-docd: same pipeline, different prompt
      → returns draft text
  → Draft shown in hyos-inspector (read-only view)
  → User clicks "Open in Writer"
    → hyos-writer opens with draft pre-loaded (user must explicitly save)
```

## Key design decisions

See `docs/adrs/` for formal Architecture Decision Records. Summary:

- **Fedora Atomic as base** — reproducibility, rollback, SELinux (ADR-0001)
- **GNOME Search Provider as first integration** — uses official, documented, stable API (ADR-0002)
- **Local-only model access in v0.1** — no cloud data leakage risk during alpha (ADR-0003)
