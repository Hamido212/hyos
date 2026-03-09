# Threat Model — HyOS v0.1

## Scope

This document covers the threat model for HyOS v0.1 in its local-only configuration, running on Fedora Atomic Desktop with GNOME and SELinux enforcing.

Out of scope for v0.1: cloud backends, multi-user systems, remote access, network-facing services.

---

## Assets

| Asset | Sensitivity | Location |
|---|---|---|
| User documents | High | `~/Documents`, `~/Downloads`, `~/Desktop` |
| SSH keys | Critical | `~/.ssh` |
| Browser credentials | Critical | `~/.mozilla`, `~/.config/chromium` |
| Secret keyrings | Critical | `~/.local/share/keyrings` |
| System configuration | High | `/etc` |
| HyOS index / cache | Medium | `~/.local/share/hyos/` |
| Ollama model weights | Low | `~/.ollama/` |
| D-Bus session | Medium | Runtime only |

---

## Trust levels

| Actor | Trust |
|---|---|
| Logged-in user | Full trust (controls policy settings) |
| HyOS user services | Medium trust (scoped, read-only, no root) |
| Ollama service | Low trust (external dependency, localhost only) |
| Document content / LLM output | Zero trust (treated as data, never executed) |
| System Bus / polkit | Trusted channel for privilege escalation |
| GNOME Shell | Trusted (same user session) |

---

## Attack surface

### Surface 1: D-Bus Session Bus interface

All HyOS services are exposed on the Session Bus. A malicious process running in the same user session could call HyOS D-Bus methods.

**Mitigations:**
- D-Bus policy files restrict which methods are callable and by which callers.
- `hyos-policyd` evaluates every task request before execution.
- Write operations are not exposed in v0.1.
- No method accepts a raw shell command or file path to execute.

### Surface 2: Document content passed to LLM

A maliciously crafted document could contain prompt injection text designed to cause `hyos-docd` to take unintended actions.

**Mitigations:**
- In v0.1, `hyos-docd` only returns text. It does not execute tool calls, write files, or make network requests based on LLM output.
- LLM output is displayed to the user and requires explicit user action to apply.
- Future agentic versions must validate all LLM-proposed actions against the policy layer before execution.

### Surface 3: Ollama HTTP endpoint

Ollama exposes a local HTTP API on `localhost:11434`. A local process could call it directly.

**Mitigations:**
- Ollama is bound to `127.0.0.1` only.
- `RestrictAddressFamilies` on HyOS services limits network access.
- Ollama runs in its own service unit with its own hardening.
- No model in v0.1 has internet access or tool-use capabilities enabled at the Ollama level.

### Surface 4: File indexer scope creep

`hyos-indexerd` could over-index sensitive files if its path restrictions are misconfigured.

**Mitigations:**
- `InaccessiblePaths=` in the service unit is the hard stop.
- Indexer configuration is initialized to the three explicitly approved paths.
- Indexer runs read-only; it cannot modify what it reads.

### Surface 5: Privilege escalation via `hyos-privileged-helperd`

The System Bus helper could be exploited to escalate privileges.

**Mitigations:**
- In v0.1, this service is a stub. No real actions are implemented.
- Every future action requires a polkit authorization check.
- polkit action files must use `auth_admin_keep` or stronger for all system-modifying actions.
- The helper binary is installed with strict SELinux type enforcement.

---

## Out-of-scope threats (v0.1)

These are real future concerns but explicitly out of scope for v0.1:

- Multi-user systems and session isolation
- Cloud backend data confidentiality
- Network-facing attack surface
- Model poisoning / supply chain attacks on Ollama weights
- Side-channel attacks via model inference timing
- Physical access attacks

---

## Residual risks accepted for v0.1

| Risk | Rationale |
|---|---|
| A local process in the same user session can call HyOS D-Bus methods | Acceptable for alpha. D-Bus policy files mitigate the most dangerous calls. |
| Ollama model output could contain harmful suggestions | Acceptable because output is displayed only; no agentic execution in v0.1. |
| No formal SELinux policy yet | Policy modules tracked but not enforced in v0.1. Accepted as known debt. |

---

## Next review trigger

This threat model must be updated before:

- Any write capability is added (file save, mail send, etc.)
- Any cloud backend is introduced
- Any agentic / tool-calling capability is introduced
- The `hyos-privileged-helperd` stub is implemented with real actions
