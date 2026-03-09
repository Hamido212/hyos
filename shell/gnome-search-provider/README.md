# hyos-search-provider

GNOME Shell Search Provider for HyOS.

## Responsibility

This component is the primary integration between HyOS and the GNOME desktop. It implements the `org.gnome.Shell.SearchProvider2` D-Bus interface, allowing HyOS results to appear natively in the GNOME Activities search overlay.

It is a **thin adapter only**. No AI logic, no indexing, no model calls. Its entire job is to translate GNOME's search protocol into HyOS D-Bus calls and format the results for GNOME.

## D-Bus interface implemented

`org.gnome.Shell.SearchProvider2` on object path `/tech/hyos/SearchProvider`.

The service acquires the well-known name `tech.hyos.SearchProvider` on the Session Bus.

## Registration

The provider is registered via:

`/usr/share/gnome-shell/search-providers/tech.hyos.SearchProvider.ini`

```ini
[Shell Search Provider]
DesktopId=tech.hyos.Inspector.desktop
BusName=tech.hyos.SearchProvider
ObjectPath=/tech/hyos/SearchProvider
Version=2
```

## Call flow

```
GNOME Shell → GetInitialResultSet(["query", "terms"])
  → Indexer.Search("query terms", 10)        [parallel]
  → Router.RunTask({type: "semantic_search"}) [parallel]
  → combine and deduplicate results
  → return result ID list to GNOME

GNOME Shell → GetResultMetas([id1, id2, ...])
  → Indexer.GetDocumentMeta(doc_id) per result
  → return [{id, name, description, gicon}, ...]

GNOME Shell → ActivateResult(id, terms, timestamp)
  → launch hyos-inspector --result-id <id>
```

## Result ID format

```
{type}:{doc_id}
```

Examples:
```
doc:sha256:3a4f9b...
action:extract_deadlines:sha256:3a4f9b...
semantic:sha256:3a4f9b...
```

## Error handling

If backend services are unavailable, `GetInitialResultSet` returns `[]`. GNOME search continues normally with results from other providers. The provider never lets a backend error propagate as an unhandled exception.

## Security

- Runs as a user service. No root.
- Minimal D-Bus surface: only session bus, only calling hyos-routerd and hyos-indexerd.
- Does not access the filesystem directly.
- D-Bus activation is the only way it starts.
