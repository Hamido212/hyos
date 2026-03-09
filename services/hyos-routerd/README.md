# hyos-routerd

Central task orchestrator for HyOS.

## Responsibility

- Accepts task requests via `org.hyos.Router1` on the Session Bus.
- Validates task parameters.
- Calls `hyos-policyd` (`org.hyos.Policy1`) to authorize every task before execution.
- Routes tasks to the appropriate backend service (`hyos-docd`, `hyos-indexerd`, or the model adapter).
- Manages job lifecycle and emits `JobUpdated` / `JobFinished` / `JobFailed` signals.
- Owns the model adapter abstraction over Ollama (all other services that need a model call through the router, not Ollama directly — except `hyos-docd` for v0.1 performance reasons).

## D-Bus interface

`org.hyos.Router1` on `/org/hyos/Router` — see [`docs/dbus/org.hyos.Router1.xml`](../../docs/dbus/org.hyos.Router1.xml).

## Capabilities

Task types supported in v0.1:

| Type | Backend |
|---|---|
| `semantic_search` | `hyos-indexerd` + Ollama reranking |
| `summarize` | `hyos-docd` |
| `extract_deadlines` | `hyos-docd` |
| `translate` | `hyos-docd` |
| `draft_reply` | `hyos-docd` |

## Security

- Runs as a user service (systemd user instance).
- No root, no System Bus access.
- Every task is evaluated by `hyos-policyd` before execution.
- Does not accept shell commands, raw script execution, or file write tasks.

## State

In-memory job map only. Jobs are not persisted across service restarts.

## Implementation notes

- D-Bus name activation via a `.service` file and a corresponding systemd user unit.
- Job IDs are random UUIDs.
- Signals are emitted per-job as processing progresses.
- Model adapter interface must be defined so future backends can be added without changing the router's public API.
