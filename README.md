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
diri init ./project --intent intent.md
diri discover ./project --intent intent.md
diri score ./project
diri plan ./project
diri self-score
diri compare before.json after.json
```

## MVP Mode

This first version uses deterministic rule-based analysis plus a mock LLM provider interface. It is useful for early project direction, gap discovery, TODO planning, and self-assessment, but it should be reviewed by a human.
