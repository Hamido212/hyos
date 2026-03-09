# HyOS SELinux Policy

This directory will contain SELinux policy modules for HyOS services.

SELinux module development is tracked as part of the Phase 4 (Policy + Hardening) milestone.

## Status

v0.1: Not yet enforced. Placeholder structure only.

## Planned modules

| Module | Covers |
|---|---|
| `hyos_routerd` | hyos-routerd process and its file contexts |
| `hyos_indexerd` | hyos-indexerd process, index files, inotify access |
| `hyos_docd` | hyos-docd process, localhost network to Ollama |
| `hyos_policyd` | hyos-policyd process, config file access |
| `hyos_search_provider` | hyos-search-provider process, D-Bus-only |

## Approach

Each HyOS service will have:
- A dedicated SELinux domain type (e.g. `hyos_routerd_t`)
- A file context for its binary (`/usr/libexec/hyos/hyos-routerd`)
- Explicit allow rules for required D-Bus names
- Deny-by-default for everything else

The aim is that `systemd-analyze security` and manual SELinux policy review confirm that no HyOS service can access resources outside its declared scope.

## References

- Fedora SELinux documentation: https://docs.fedoraproject.org/en-US/quick-docs/selinux-getting-started/
- SELinux policy writing guide: https://fedoraproject.org/wiki/SELinux/WritingPolicy
- `audit2allow` for iterative policy development during testing
