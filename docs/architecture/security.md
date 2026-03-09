# Security Architecture

## Principle

Security is not a feature added on top — it is the architecture. HyOS is designed to be present everywhere in the desktop. That makes security discipline mandatory from day one, not something to retrofit.

The core rule: **an AI service that runs everywhere must have the smallest possible blast radius when something goes wrong.**

---

## Security boundaries

### Boundary 1: No root for AI processes

All HyOS AI services run as unprivileged user-scoped systemd services. They do not call `sudo`, `pkexec`, or `setuid` binaries during normal operation.

The only component allowed on the System Bus and capable of privileged actions is `hyos-privileged-helperd`, and every action it takes is gated behind a polkit authorization check. In v0.1, this service exists as a stub only.

### Boundary 2: Session Bus for normal work, System Bus only for privileged actions

```
Session Bus: hyos-routerd, hyos-indexerd, hyos-docd, hyos-policyd,
             hyos-search-provider
System Bus:  hyos-privileged-helperd (stub in v0.1)
```

Session Bus services cannot acquire System Bus names or escape their user session.

### Boundary 3: Local-first as default

In v0.1, all processing is local:

- Document text extraction: local
- Semantic search: local (Ollama)
- Summarization, translation, drafting: local (Ollama)
- Index storage: local (`~/.local/share/hyos/index/`)

No data leaves the machine in v0.1. Cloud backends are explicitly out of scope and must be explicitly enabled in future versions via a user-visible policy setting.

### Boundary 4: Read-only, scoped file access

`hyos-indexerd` and `hyos-docd` have read-only access to the following paths only:

- `~/Documents`
- `~/Downloads`
- `~/Desktop`

They do not read `/etc`, `~/.ssh`, `~/.gnupg`, `~/.config/chromium`, `~/.mozilla`, or any other sensitive user directory. This is enforced by systemd `ReadOnlyPaths=` and `InaccessiblePaths=` directives.

### Boundary 5: No silent side effects

The following actions can never happen silently in v0.1:

| Action | Status |
|---|---|
| Overwrite an existing file | Blocked |
| Delete a file | Blocked |
| Send an email | Blocked |
| Execute a shell command | Blocked |
| Install a package | Blocked |
| Modify system configuration | Blocked (stub only) |
| Access SSH keys | Blocked (InaccessiblePaths) |
| Access browser cookies/passwords | Blocked (InaccessiblePaths) |
| Make network requests outside localhost | Blocked (RestrictAddressFamilies) |

### Boundary 6: polkit for every privileged action

Any action that requires elevated privilege must go through `hyos-privileged-helperd` on the System Bus, which calls `polkit` to authorize the action. The action ID namespace is `tech.hyos.action.*`.

### Boundary 7: SELinux type enforcement

HyOS processes and their file paths will have dedicated SELinux types. This allows policy to restrict which system resources each HyOS service can access, independently of DAC permissions.

In v0.1, SELinux policy modules live in `packaging/selinux/` and are tracked even if not yet fully enforced.

### Boundary 8: systemd sandboxing

All HyOS user services ship with hardened `systemd.exec` settings. The minimum required set:

```ini
[Service]
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
RestrictAddressFamilies=AF_UNIX
MemoryDenyWriteExecute=yes
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
LockPersonality=yes
RestrictNamespaces=yes
RestrictRealtime=yes
RemoveIPC=yes
```

Services that need network access (e.g. calling Ollama) additionally need `AF_INET` in `RestrictAddressFamilies` — but only those services.

Hardening scores are tracked via `systemd-analyze security hyos-*.service` and reviewed before each release.

---

## Threat categories and mitigations

### T1: Prompt injection leading to file writes or command execution

**Mitigation:** Write actions are blocked at the service level, not just the UI level. `hyos-docd` returns text — it does not write files. The user must explicitly copy/open generated content. There is no mechanism for a prompt to cause a file write in v0.1.

### T2: Local model exfiltrating data

**Mitigation:** Ollama runs on localhost only. `RestrictAddressFamilies=AF_UNIX AF_INET` on `hyos-docd` allows calling `localhost:11434` but network egress from Ollama itself is constrained by its own service unit. In v0.1, Ollama has no configured external server.

### T3: HyOS service privilege escalation

**Mitigation:** `NoNewPrivileges=yes` on all services prevents acquiring new capabilities. `ProtectSystem=strict` prevents writing to system paths. SELinux type enforcement adds a MAC layer.

### T4: Malicious document triggering code execution

**Mitigation:** Text extraction is performed with hardened libraries. The extracted plain text is passed to Ollama. No HyOS service executes macros, scripts, or embedded content from documents. All text is treated as data.

### T5: D-Bus surface abuse

**Mitigation:** All HyOS D-Bus interfaces are owned services (not peer-to-peer). Callers on the Session Bus are limited to the same user session. D-Bus policy files restrict which names can be claimed and which methods can be called. `hyos-policyd` evaluates every task before execution.

### T6: Indexer accessing sensitive files

**Mitigation:** `InaccessiblePaths=` in `hyos-indexerd.service` lists paths that must never be indexed:

```ini
InaccessiblePaths=/etc /root %h/.ssh %h/.gnupg %h/.config/chromium
    %h/.mozilla %h/.local/share/keyrings %h/.kube %h/.aws %h/.azure
```

---

## Security review checklist (per release)

- [ ] `systemd-analyze security` score reviewed for all HyOS services
- [ ] `InaccessiblePaths` list reviewed against new filesystem regions
- [ ] No new network access added without explicit policy approval
- [ ] No new write paths added without explicit confirmation UI
- [ ] SELinux policy modules compile and are not in permissive mode
- [ ] polkit action files reviewed for overly broad `allow_any` grants
- [ ] Threat model updated if new capabilities were added
- [ ] Dependency audit (Ollama version, document parsing libraries)
