# ADR-0001: Use Fedora Atomic Desktop as the base system

**Status:** Accepted
**Date:** 2026-03-09

## Context

HyOS needs a Linux base that is:

- Stable and reproducible for an experimental AI system layer
- Rollback-capable in case HyOS system packages break something
- SELinux-enforcing by default
- Compatible with systemd user services and D-Bus session architecture
- Supported long-term with security updates

The options considered:

| Option | Pros | Cons |
|---|---|---|
| Fedora Atomic Desktop (Silverblue) | Image-based, rollback, SELinux, rpm-ostree layering, reproducible | Layered packages require rebuild/rebase for upgrades |
| Ubuntu (standard) | Large ecosystem, familiar, snap support | Mutable by default, AppArmor instead of SELinux, no easy rollback |
| Arch Linux | Very up-to-date packages | No rollback, no atomic updates, high maintenance |
| NixOS | Fully reproducible, rollback | Complex learning curve, different ecosystem, harder GNOME integration |
| Debian stable | Stability | Very old packages, no atomic updates |

## Decision

Use **Fedora Atomic Desktop (Silverblue)** as the base system for HyOS development and as the target for HyOS packaging.

## Rationale

1. **Image-based updates and rollback:** If a HyOS system package causes instability, the user can roll back with `rpm-ostree rollback`. This is essential for an OS-level AI project.

2. **SELinux enforcing by default:** Fedora with SELinux means HyOS can build SELinux policy modules from day one, not retrofit them later.

3. **Layerable packages via rpm-ostree:** `rpm-ostree install` allows adding HyOS packages to the image without breaking the atomic update model.

4. **GNOME as default shell:** Silverblue ships GNOME, which has the Search Provider API and other integration points HyOS needs.

5. **systemd user services:** Full support for user-scoped services and D-Bus activation.

6. **Community and tooling:** Fedora has strong tooling for building custom OSTree images (image-builder, Containerfiles for custom images), which is the path to a future HyOS distribution image.

## Consequences

- Development requires a Fedora Atomic machine or VM (not Ubuntu, not macOS).
- HyOS packaging targets RPM initially, not Debian packages.
- Testing must happen on Fedora to catch SELinux and systemd unit issues.
- A custom HyOS image based on Fedora Atomic is the long-term goal for `hyos.tech` downloads.
