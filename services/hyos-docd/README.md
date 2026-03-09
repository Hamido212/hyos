# hyos-docd

Document workflow service for HyOS.

## Responsibility

- Extracts plain text from documents (PDF, DOCX, ODT, TXT, HTML).
- Constructs structured prompts for each workflow action.
- Calls Ollama at `localhost:11434/api/generate` with the prompt.
- Returns structured results over D-Bus.
- Is stateless between calls — no document cache, no session state.

## D-Bus interface

`org.hyos.Documents1` on `/org/hyos/Documents` — see [`docs/dbus/org.hyos.Documents1.xml`](../../docs/dbus/org.hyos.Documents1.xml).

## Workflow actions (v0.1)

| Method | What it does |
|---|---|
| `SummarizeUri` | Extract text → prompt for structured summary |
| `ExtractDeadlinesUri` | Extract text → prompt for dates and deadlines as structured list |
| `TranslateUri` | Extract text → prompt for translation into target language |
| `DraftReplyUri` | Extract text → prompt for a reply draft in the given tone |
| `ProcessText` | Apply any of the above to caller-supplied text (no file I/O) |

## Security

- Runs as a user service. No root.
- `ReadOnlyPaths=~/Documents ~/Downloads ~/Desktop` — same as indexerd.
- `InaccessiblePaths` blocks sensitive directories.
- Calls with URIs outside allowed paths return `org.hyos.Error.AccessDenied`.
- Calls Ollama only on `localhost:11434`. No other network access.
- Does not write files. Returns data only.
- Document content is passed to Ollama as prompt text. It is NOT executed.

## Prompt design

Prompts must be structured to:
1. Keep system prompt and user content clearly separated.
2. Instruct the model to return structured output (JSON where applicable).
3. Never include instructions that could be overridden by document content.

Prompt injection from document content is a known risk. Mitigation: extracted text is clearly delimited and labeled as "untrusted document content" in the prompt. LLM output is returned raw to the UI (user decides what to do with it).

## Ollama interaction

```
POST http://127.0.0.1:11434/api/generate
Content-Type: application/json

{
  "model": "mistral",
  "prompt": "...",
  "stream": false
}
```

Model name is configurable via `~/.config/hyos/docd.conf`. Default: `mistral`.

## Implementation notes

- Text extraction happens before calling Ollama. If extraction fails, return an error — do not send binary data to the model.
- Enforce a maximum input token estimate before calling Ollama to avoid timeout on very large documents.
- In v0.1, all calls to Ollama are synchronous (stream: false). D-Bus method call blocks until the response is ready.
