# GNOME Search Provider Integration

## Overview

The GNOME Search Provider is the primary integration point between HyOS and the GNOME desktop in v0.1. It allows HyOS results to appear natively in GNOME Activities search alongside apps, files, and settings.

This document describes how the HyOS Search Provider works and how it integrates with the rest of the HyOS runtime.

## GNOME Search Provider protocol

GNOME Shell manages search centrally. When the user types in the Activities overlay, GNOME calls all registered search providers over D-Bus using the `org.gnome.Shell.SearchProvider2` interface.

The interface requires implementing:

| Method | Signature | Description |
|---|---|---|
| `GetInitialResultSet` | `(as) -> as` | Called with the search terms array; return a list of result IDs |
| `GetSubsearchResultSet` | `(as, as) -> as` | Called with previous result IDs + refined terms; return filtered IDs |
| `GetResultMetas` | `(as) -> aa{sv}` | Called with result IDs; return metadata dict per ID |
| `ActivateResult` | `(s, as, u) -> ()` | Called when user activates a result; open the result |
| `LaunchSearch` | `(as, u) -> ()` | Called when user clicks "show all results"; open search UI |

`GetResultMetas` returns a dict per result with the following keys:

```
id:          string
name:        string
description: string (optional)
gicon:       string (serialized GIcon, optional)
clipboardText: string (optional, for copy actions)
```

## Registration

Providers are registered via a `.ini` file placed in:

```
$(datadir)/gnome-shell/search-providers/
```

Example: `/usr/share/gnome-shell/search-providers/tech.hyos.SearchProvider.ini`

```ini
[Shell Search Provider]
DesktopId=tech.hyos.Inspector.desktop
BusName=tech.hyos.SearchProvider
ObjectPath=/tech/hyos/SearchProvider
Version=2
```

The `BusName` must match the D-Bus service name that `hyos-search-provider` acquires.

## HyOS Search Provider design

The Search Provider is a thin adapter. It contains no business logic. Its only job is to translate GNOME's search protocol into HyOS D-Bus calls.

```
GNOME Shell
  ↓ GetInitialResultSet(["last", "letter"])
hyos-search-provider
  ↓ org.hyos.Indexer1.Search("last letter", limit=20)       [concurrent]
  ↓ org.hyos.Router1.RunTask({type: "semantic_search", ...}) [concurrent]
  ↑ combined result IDs returned to GNOME
  ↓ GetResultMetas([id1, id2, id3])
  ↑ {id, name, description, gicon} per result
  ↓ ActivateResult(id1, terms, timestamp)
    → launch hyos-inspector --result-id id1
```

## Result types

In v0.1, three result types are defined:

### `doc` — Document match

A file matched by the local index.

```
name:        "Bescheid_August.pdf"
description: "Frist bis 14.10. · ~/Downloads · 3 days ago"
gicon:       "application-pdf"
```

Activating opens HyOS Inspector with the document loaded.

### `action` — AI action

A suggested AI workflow for the current search context.

```
name:        "Extract deadlines from recent letters"
description: "HyOS · AI action"
gicon:       "tech.hyos.Inspector"
```

Activating runs the action and opens HyOS Inspector with the result.

### `semantic` — Semantic document match

A document matched by meaning, not filename.

```
name:        "Letter about appointment confirmation"
description: "Terminbestätigung_2025.pdf · ~/Documents"
gicon:       "text-x-generic"
```

Activating opens the document in HyOS Inspector.

## Result ID format

Result IDs are stable, opaque strings. Format:

```
{type}:{doc_id_or_action_id}
```

Examples:
```
doc:sha256:3a4f...
action:extract_deadlines:sha256:3a4f...
semantic:sha256:3a4f...
```

## Error handling

If `hyos-indexerd` or `hyos-routerd` is unavailable, the provider returns an empty result set. It does not show an error in the GNOME search UI — it simply yields no results. This avoids breaking the GNOME search experience when HyOS services are not running.
