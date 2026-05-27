# DIRI

DIRI is not a generic code quality analyzer.

DIRI measures how well a codebase reproduces the result that the developer intended to achieve.

## Core Idea

Code is evaluated against developer intent, not abstract cleanliness.

DIRI asks:

```text
How well does this code reproduce the result the developer actually wanted?
```

It does not reward clean architecture, test count, or short functions unless they help reproduce the expected result.

## DIRI for Vibecoders

You say what you want. The AI builds it. DIRI tells you how close it landed — and what's missing.

Vibe coding moved the bottleneck from "can you write the code" to "does the result match what you meant". DIRI is the instrument for that gap: a fidelity index between your intent and the result, so you can verify an agent's output without reading every line.

See [`docs/VISION.md`](docs/VISION.md) for the full vision, the vibecoder loop, and the roadmap.

## Commands

```bash
diri init . --intent intent.md
diri discover . --intent intent.md
diri score .
diri plan .
diri self-score
diri compare before.json after.json
diri operator-packet
diri operator-prompt
diri install-operator all
```

From inside a project directory, the project argument defaults to the current directory:

```bash
diri init
diri score
diri plan
```

`diri self-score` is not a separate evaluator. It runs the same DIRI scoring flow on the DIRI project itself, using DIRI's own `.diri/intent.json` and `.diri/expected_result.json`.

## Install CLI After Clone

DIRI is designed to be installed as a local developer CLI with `uv tool`.

Windows PowerShell:

```powershell
git clone https://github.com/sonofthenation/DIRI.git
cd DIRI
.\scripts\install-cli.ps1
diri --help
```

macOS/Linux:

```bash
git clone https://github.com/sonofthenation/DIRI.git
cd DIRI
sh scripts/install-cli.sh
diri --help
```

For development without installing the command globally, use:

```bash
uv run diri --help
```

## DIRI Operator Bridge

DIRI can prepare local AI coding agents to speak in DIRI-mode for evaluation requests.

```bash
diri operator-packet
diri operator-prompt
diri install-operator all
```

`diri operator-packet` writes:

```text
.diri/operator/operator_packet.json
.diri/operator/DIRI_OPERATOR.md
```

`diri install-operator all` installs thin bridge files for common agents:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.cursor/rules/diri.mdc
.windsurf/rules/diri.md
.github/copilot-instructions.md
```

These files do not turn an AI assistant into DIRI permanently. They instruct the assistant to enter temporary DIRI-mode only when the user asks for a DIRI evaluation, use `.diri/operator/operator_packet.json` as evidence, speak as DIRI for that response, and then return to normal assistant mode.

## Intent Understanding Engine

DIRI discovers developer intent through whichever backend is available, in this order (see the [roadmap](docs/VISION.md#roadmap-to-the-bar)):

1. **Claude API** — semantic understanding via the `anthropic` SDK. Used when `ANTHROPIC_API_KEY` is set and `pip install 'diri[llm]'` was run.
2. **Claude Code (local CLI)** — uses your **already-installed Claude Code** and its existing subscription login by shelling out to the official `claude` binary in headless mode. **No API key required.** Used automatically when no API key is set but `claude` is on your `PATH`.
3. **Heuristic** — deterministic rule-based analysis. Fully inspectable, zero setup. The fallback whenever neither Claude backend is available or a call fails.

`diri init` / `diri discover` print which engine ran, e.g. `Intent engine: Claude Code (local CLI)`.

```bash
# Option A — reuse your installed Claude Code (no API key)
diri init . --intent intent.md

# Option B — Claude API
pip install 'diri[llm]'
export ANTHROPIC_API_KEY=...
diri init . --intent intent.md
```

Environment overrides:
- `DIRI_LLM_BACKEND` — force a backend: `api`, `claude-code`, or `off`.
- `DIRI_LLM_MODEL` — model id/alias (default `claude-opus-4-7`).
- `DIRI_CLAUDE_BINARY` — path/name of the Claude Code binary (default `claude`).
- `DIRI_LLM_DISABLE=1` — force heuristic mode.

Scoring itself remains rule-based for now and should be reviewed by a human.
