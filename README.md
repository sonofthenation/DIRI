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

## MVP Mode

This first version uses deterministic rule-based analysis plus a mock LLM provider interface. It is useful for early project direction, gap discovery, TODO planning, and self-assessment through the same scoring loop, but it should be reviewed by a human.
