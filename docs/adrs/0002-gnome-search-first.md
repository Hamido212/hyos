# ADR-0002: GNOME Search Provider as the first desktop integration point

**Status:** Accepted
**Date:** 2026-03-09

## Context

HyOS needs to demonstrate that AI is "in the desktop" — not just another app or chat window. The question is: what is the right first integration point?

Options considered:

| Integration point | API stability | Risk |
|---|---|---|
| GNOME Shell Extension | Unstable (breaks every GNOME version) | High |
| Custom compositor / Wayland compositor | Massive engineering effort | Very high |
| KRunner (KDE) | KDE-specific, forks the platform target | Medium |
| GNOME Search Provider | Stable, documented, official | Low |
| Standalone launcher app | No desktop integration | None (too weak) |
| Global keyboard shortcut via libinput/Portal | Works but limited surface | Medium |

## Decision

Use the **GNOME Search Provider** (`org.gnome.Shell.SearchProvider2`) as the first and primary desktop integration point for HyOS v0.1.

## Rationale

1. **Official and stable API:** The Search Provider D-Bus interface is documented by GNOME Developer Documentation and has been stable across GNOME versions. It does not require a Shell Extension, does not inject into the Shell process, and does not break on GNOME updates.

2. **High-value surface:** GNOME search is a central UX concept — the Activities overlay is where users go to find things. Appearing here means HyOS results are part of the native search experience, not a separate window.

3. **Low coupling:** The provider is a separate process. If it crashes, GNOME search still works. If GNOME updates, the provider only needs to re-register.

4. **Activates the entire HyOS runtime:** The Search Provider activates `hyos-routerd` and `hyos-indexerd` via D-Bus, meaning the first meaningful demo can be: user types → HyOS result appears → user clicks → HyOS Inspector opens with full document analysis.

5. **No Shell Extension required for v0.1:** Shell Extensions are fragile and require signing for distribution. A Search Provider requires only a `.ini` file and a D-Bus service, which is trivially packaged in an RPM.

## Consequences

- v0.1 is GNOME-specific. KDE/Plasma integration is out of scope.
- The Search Provider must handle D-Bus errors gracefully (return empty results, never crash GNOME search).
- Result rendering is controlled by GNOME Shell (we cannot make results look custom). Richness is limited to: name, description, icon.
- Full custom UI lives in HyOS Inspector (opened via `ActivateResult`), not in the search overlay itself.
