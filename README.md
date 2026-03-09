# HyOS

**HyOS is a Linux-native AI shell where search, documents, text creation, and automation are built into the desktop — not bolted on as a chat window.**

---

## What is HyOS?

HyOS is not a new Linux distribution or a new kernel. It is a **Linux-native AI shell layer** built on top of Fedora Atomic Desktop (Silverblue) and GNOME. AI is integrated into the operating surface — search, file workflows, text creation, agent services — with strict, explicit security boundaries.

HyOS v0.1 proves three things:

1. **AI in search** — GNOME search returns semantic document results and AI-powered actions, not just filenames.
2. **AI in a document workflow** — Local documents can be analyzed: summary, deadline extraction, translation, reply drafting.
3. **AI built with security discipline** — Local-first, no silent root actions, no uncontrolled agent behavior.

---

## Architecture overview

HyOS is structured in five layers:

| Layer | What lives here |
|---|---|
| Base | Fedora Atomic Desktop, GNOME, Wayland, systemd, SELinux |
| Session | HyOS Search Provider, desktop files |
| Runtime | `hyos-routerd`, `hyos-indexerd`, `hyos-docd`, `hyos-policyd` |
| Model | Ollama (local only, v0.1) |
| Security | XDG Portals, polkit, SELinux, systemd hardening |

All runtime services communicate over **D-Bus**. No service calls another directly through shared memory or sockets except where D-Bus is impractical and an explicit interface is agreed upon.

```
┌─────────────────────────────────────────────────────────┐
│                     GNOME Shell                          │
│          (Search Provider activated via D-Bus)           │
└────────────────────┬────────────────────────────────────┘
                     │ org.gnome.Shell.SearchProvider2
                     ▼
┌─────────────────────────────────────────────────────────┐
│              hyos-search-provider                        │
│          (thin adapter, Session Bus)                     │
└──────────┬──────────────────────┬───────────────────────┘
           │ org.hyos.Router1     │ org.hyos.Indexer1
           ▼                      ▼
┌──────────────────┐   ┌──────────────────────────────────┐
│  hyos-routerd    │   │  hyos-indexerd                   │
│  (orchestrator)  │   │  (local content index)           │
└────────┬─────────┘   └──────────────────────────────────┘
         │ org.hyos.Documents1 / org.hyos.Policy1
         ▼
┌──────────────────┐   ┌──────────────────────────────────┐
│  hyos-docd       │   │  hyos-policyd                    │
│  (doc workflows) │   │  (policy decisions)              │
└────────┬─────────┘   └──────────────────────────────────┘
         │ HTTP (localhost only)
         ▼
┌──────────────────────────────────────────────────────────┐
│  Ollama                                                   │
│  (local model service, localhost:11434)                   │
└──────────────────────────────────────────────────────────┘
```

See [`docs/architecture/overview.md`](docs/architecture/overview.md) for the full architecture document.

---

## Repository layout

```
hyos/
  docs/
    architecture/         System design documents
    adrs/                 Architecture Decision Records
    dbus/                 D-Bus interface definitions (XML)
  services/
    hyos-routerd/         Central task orchestrator
    hyos-indexerd/        Local content indexer
    hyos-docd/            Document workflow service
    hyos-policyd/         Policy engine
  shell/
    gnome-search-provider/  GNOME Shell search integration
    desktop-files/
    search-provider-config/
  apps/
    hyos-inspector/       Result viewer UI (GTK/libadwaita)
    hyos-writer/          AI-integrated text editor
  packaging/
    systemd/              systemd unit files
    polkit/               polkit action files
    selinux/              SELinux policy modules
    fedora/               Fedora/rpm-ostree packaging
  scripts/
    dev/                  Developer setup scripts
    test/                 Test helpers
    demo/                 Demo flow scripts
  tests/
    integration/
    fixtures/
```

---

## Security model

Security is not a feature layer — it is the architecture.

**Hard rules for v0.1:**

- AI processes do not run as root under any normal circumstances.
- All AI services run on the **Session Bus** (user-scoped), except `hyos-privileged-helperd` (System Bus, stub only in v0.1).
- v0.1 is **local-only**. No cloud API calls. No silent network access.
- The indexer and document service have read-only access to `~/Documents`, `~/Downloads`, and `~/Desktop` only.
- No action silently overwrites files, sends mail, executes shell commands, installs packages, or changes system configuration. All such actions require explicit confirmation.
- Privileged actions go through polkit. No exceptions.

systemd unit files ship with the following minimum hardening:

```ini
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
RestrictAddressFamilies=AF_UNIX
MemoryDenyWriteExecute=yes
```

See [`docs/architecture/security.md`](docs/architecture/security.md) and [`docs/architecture/threat-model.md`](docs/architecture/threat-model.md).

---

## Services

| Service | Bus | Role |
|---|---|---|
| `hyos-routerd` | Session | Task orchestrator, capability registry |
| `hyos-indexerd` | Session | Local file content index |
| `hyos-docd` | Session | Document analysis and drafting |
| `hyos-policyd` | Session | Policy decisions (local-only, read-only, confirm-on-write) |
| `hyos-privileged-helperd` | System | Admin actions via polkit (stub in v0.1) |
| `ollama` | — | Local model service (external dependency) |

---

## D-Bus interfaces

| Interface | Object path |
|---|---|
| `org.hyos.Router1` | `/org/hyos/Router` |
| `org.hyos.Indexer1` | `/org/hyos/Indexer` |
| `org.hyos.Documents1` | `/org/hyos/Documents` |
| `org.hyos.Policy1` | `/org/hyos/Policy` |
| `org.hyos.Privileged1` | `/org/hyos/Privileged` |

Interface definitions are in [`docs/dbus/`](docs/dbus/).

---

## v0.1 roadmap

| Phase | Days | Goal | Deliverable |
|---|---|---|---|
| 0 — Foundation | 1–15 | Dev environment, Ollama, monorepo, ADRs, D-Bus hello-world | HyOS Router responds on Session Bus |
| 1 — Search | 16–30 | GNOME Search Provider + local indexer + first AI results | Search "last letter" → HyOS returns a document result |
| 2 — Document | 31–45 | `hyos-docd` with Summarize / Deadlines / Translate / Draft | A letter is analyzed locally |
| 3 — Inspector | 46–60 | GTK/libadwaita result viewer | `ActivateResult` opens HyOS Inspector |
| 4 — Policy + Hardening | 61–75 | `hyos-policyd`, systemd hardening, SELinux prep | Every action has a verifiable policy decision |
| 5 — Demo Alpha | 76–90 | RPM/layering, hyos.tech landing page, demo flow | End-to-end: Search → Analyze → Draft |

**v0.1 success criterion:**

> "I can search in GNOME for a real document, HyOS understands the context, analyzes it locally, and opens a structured workflow — without launching a chat window."

---

## What HyOS is not (v0.1)

- Not a new kernel or window manager
- Not a full Linux distribution with an installer
- Not "AI controls everything"
- No browser cookie / password / SSH key integration
- No cloud workflows
- No free-running agents with shell access

---

## Development setup

HyOS targets **Fedora Atomic Desktop (Silverblue)**. On Atomic hosts the root filesystem is immutable — `sudo dnf install` does not persist across updates. The correct setup is split into three phases.

### Phase 1 — Host prerequisites (rpm-ostree, one-time)

Layer the required runtime packages onto the host image. This requires a reboot.

```bash
bash scripts/dev/host-setup.sh
# Follow the reboot prompt, then continue with Phase 2.
```

What this does: `rpm-ostree install python3-dbus python3-gobject poppler-utils python3-pip`

### Phase 2 — Dev environment (Toolbx, no reboot)

Toolbx provides a mutable Fedora container for development work (editing, linting, running unit tests). Services themselves run on the host — not inside the container.

```bash
toolbox create hyos-dev
toolbox enter hyos-dev
bash scripts/dev/toolbox-setup.sh
```

### Phase 3 — Deploy to session (host, after reboot)

Installs the HyOS Python packages to the host user Python, deploys D-Bus activation files and systemd user units, registers the GNOME Search Provider, and starts all services.

```bash
bash scripts/dev/session-setup.sh
```

### Verify

```bash
# Smoke test — checks all five D-Bus services
bash scripts/test/smoke.sh

# First vertical slice — requires a PDF in ~/Downloads/ and Ollama running
# See docs/testing/silverblue-testplan.md
```

### Ollama

```bash
# Install (run once on the host, outside toolbox)
curl -fsSL https://ollama.com/install.sh | sh
systemctl --user enable --now ollama
ollama pull mistral
```

---

## License

[MIT](LICENSE)

---

## Contributing

HyOS is in early alpha. The architecture is not yet stable. Before contributing, read:

- [`docs/architecture/overview.md`](docs/architecture/overview.md)
- [`docs/architecture/security.md`](docs/architecture/security.md)
- [`docs/architecture/threat-model.md`](docs/architecture/threat-model.md)
- ADRs in [`docs/adrs/`](docs/adrs/)

All contributions must respect the security model. Pull requests that bypass policy gates, add silent write actions, or introduce root-requiring runtime behavior will not be merged.
