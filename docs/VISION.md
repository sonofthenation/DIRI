# DIRI for Vibecoders

> You say what you want. The AI builds it. DIRI tells you how close it landed — and what's missing.

## The vibe coding trust gap

Vibe coding moved the bottleneck.

For decades the hard part was *writing* the code. Now an AI writes it. You describe what
you want in plain language, the agent produces a working app, and you run it. The new
hard part is a different question:

```text
Did the result actually reproduce what I meant?
```

A vibecoder rarely reads the code. They look at the running app and hope it matches the
intent in their head. There is no instrument for that gap. "It runs" is not "it's what I
asked for." Tests check that code does what the code says. Linters check style. Neither
checks whether the *product* reproduces the *intent*.

That missing instrument is the whole point of DIRI.

## DIRI is the missing instrument

DIRI is the **Developer Intent Reproduction Index**: a measure of how closely a codebase
reproduces the result the developer intended to achieve.

It does not reward clean architecture, test count, or short functions unless those help
reproduce the intended result. It scores one thing — fidelity to intent — and tells you
where the result drifts from what you asked for.

For a vibecoder, that is exactly the missing feedback loop: a way to verify the agent's
output against your intent without reading every line.

## How it works, honestly

The loop is small and inspectable:

```text
intent.md  →  discovered intent  →  expected result  →  6-metric score  →  gaps  →  TODO
```

- **Intent discovery** reads your `intent.md` and extracts what you actually want —
  functional, visual, emotional, and technical targets (`diri/intent/intent_discovery.py`).
- **Expected result** turns that intent into concrete success and failure conditions
  (`diri/result_model/`).
- **Scoring** rates the project on six weighted dimensions — intent match, functional
  reproduction, behavioral reproduction, visual/UX reproduction, constraint respect, and
  completeness (`diri/constants.py`, `diri/core/levels.py`).
- **Gaps and TODO** tell you what's missing and what to fix next (`diri/planner/`).

Where it stands today, plainly: intent discovery is currently **deterministic keyword
matching**, and the LLM provider is a **stub** (`diri/llm/openai_provider.py` is not yet
implemented). That makes Stage 1 transparent and predictable, but it does not yet
*understand* intent the way a model could. We say so openly — credibility comes from
honesty about the current limits, not from hiding them. See the roadmap below for where
this goes.

## The vibecoder loop

In practice it looks like this:

```text
1. Write intent.md   — describe what you want, in your own words
2. Let the agent build it
3. diri score        — get a fidelity score, gaps, and a TODO list
4. Hand the gaps back to the agent — "fix these"
5. diri score again  — watch the index climb toward your intent
```

The **Operator Bridge** closes the loop tighter. With `diri install-operator all`, the
same AI agent that wrote the code can enter a temporary DIRI-mode and critique its own
output against your intent — using `.diri/operator/operator_packet.json` as the source
of truth — then return to building. Intent in, result out, fidelity measured, by the same
tools you already vibe with.

## Roadmap to the bar

Three honest stages, each tied to real code:

- **Stage 1 — Transparent baseline (now).** Deterministic, rule-based discovery and
  scoring. Fully inspectable, zero black box. Good for early direction, gap discovery,
  and self-assessment through the same scoring loop.
- **Stage 2 — A real intent-understanding engine.** Implement a working `LLMProvider`
  (fill the `diri/llm/provider.py` / `openai_provider.py` stub) so intent discovery and
  scoring use semantic understanding instead of keyword lists. This is the single biggest
  lever: it's the difference between matching words and understanding meaning.
- **Stage 3 — Closed-loop fidelity.** Score-driven auto-fix through the Operator Bridge,
  and a public benchmark of intent reproduction so the index means the same thing across
  projects.

## Why open

DIRI is built to be read.

The model is nanoGPT: small enough to hold in your head, readable end to end, hackable in
an afternoon, and it teaches one idea cleanly. nanoGPT teaches how a transformer trains.
DIRI teaches a different lesson:

```text
Evaluate intent, not cleanliness.
```

That lesson matters most to vibecoders, who are often building real things without a
traditional engineering background. DIRI gives them a vocabulary and an instrument for the
only question that matters to them — *did I get what I meant?* — and it does it in the
open, where anyone can inspect, learn from, and improve it.
