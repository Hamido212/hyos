# hyos-policyd

Policy engine for HyOS.

## Responsibility

- Evaluates whether a proposed action is permitted under the current policy mode.
- Returns `allow`, `deny`, or `require_confirmation` per action.
- Manages the current policy mode.
- Logs policy decisions for auditability.

## D-Bus interface

`org.hyos.Policy1` on `/org/hyos/Policy` — see [`docs/dbus/org.hyos.Policy1.xml`](../../docs/dbus/org.hyos.Policy1.xml).

## Policy modes (v0.1)

| Mode | Rules |
|---|---|
| `local-only` | No network access. Ollama on localhost is allowed. No cloud APIs. |
| `read-only` | No file writes, no mail sends, no shell execution, no package installs. |
| `confirm-on-write` | (Future) Write actions require explicit user confirmation UI. |

v0.1 always runs `local-only` **and** `read-only` simultaneously. These modes cannot be disabled in v0.1 without modifying source code.

## Evaluation logic (v0.1)

```
action.network == true AND action.network_target != "localhost"  → DENY
action.write == true                                              → DENY
action.privileged == true                                         → DENY
otherwise                                                         → ALLOW
```

## Security

- Runs as a user service. No root.
- Fast (in-memory decision, no I/O on the critical path).
- Policy configuration is stored in `~/.config/hyos/policy.conf` (TOML).
- The configuration file is not writable by D-Bus callers — only by the user directly or by a future Settings UI with explicit user action.

## Configuration (v0.1 defaults)

```toml
[policy]
mode = "local-only"
allow_localhost_network = true
allow_writes = false
allow_shell_execution = false
allow_privileged = false
```

## Implementation notes

- `Evaluate` must be fast. It is called on every task request.
- `ExplainLastDecision` is per-caller (tracked by D-Bus peer unique name).
- All decisions (allow and deny) should be logged to `journald` at `debug` level.
- Denied actions at `info` level.
