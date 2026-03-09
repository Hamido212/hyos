# ADR-0003: Local-only model access in v0.1

**Status:** Accepted
**Date:** 2026-03-09

## Context

HyOS needs an AI model backend. The options:

| Option | Pros | Cons |
|---|---|---|
| Local model via Ollama | No data leaves machine, no API cost, works offline | Limited model quality, requires hardware |
| OpenAI API | Highest quality, easy to integrate | Data leaves machine, API cost, internet required, privacy concern |
| Anthropic / Gemini / other cloud | High quality | Same concerns as OpenAI |
| Mixed (local + cloud fallback) | Best of both | Complex policy, harder to reason about privacy |

## Decision

**v0.1 is local-only.** All model inference runs through Ollama on `localhost:11434`. No cloud API keys, no external network calls for AI inference.

## Rationale

1. **Privacy-first on alpha:** HyOS will analyze users' personal documents — letters, bills, government notices, medical documents. Sending this data to a cloud API without explicit user consent in an alpha product is unacceptable.

2. **No API cost risk:** An alpha that runs up API bills is not safe to release.

3. **Architecture proof:** The goal of v0.1 is to prove the architecture — the integration with GNOME search, the document workflow, the security model. This can be proven with local models. Quality gaps are expected and acceptable in alpha.

4. **Forces good abstraction:** Requiring all model access to go through a local adapter in `hyos-routerd` forces a clean model abstraction layer. Adding a cloud backend in v0.2 means implementing the same adapter interface, not refactoring everything.

5. **No network security surface:** `RestrictAddressFamilies=AF_UNIX` (or `AF_UNIX AF_INET` limited to localhost) on all services means no accidental data exfiltration via network.

## Consequences

- Model quality will be limited by what runs locally (Mistral, Llama, Gemma class models).
- Hardware requirements: users need enough RAM to run a 7B–13B parameter model. This is a known limitation for v0.1.
- The Ollama abstraction in `hyos-routerd` must be clearly marked as `ModelAdapter` so v0.2 can introduce `CloudModelAdapter` behind a policy gate.
- Future cloud integration must be:
  - Opt-in, not default
  - Visible in UI (which requests are going where)
  - Policy-controlled (`hyos-policyd` must block cloud access if mode is `local-only`)
  - Per-request consent for sensitive document types
