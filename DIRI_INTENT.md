# DIRI — Developer Intent Reproduction Index

DIRI is a developer CLI that measures how well a codebase reproduces the result the developer intended to achieve, not generic code quality.

Required features:
- diri init creates a .diri workspace with developer intent and expected result models
- diri discover re-derives developer intent from notes and project signals
- diri score evaluates a project against its intent and writes a DIRI report
- diri plan turns the latest DIRI report into a prioritized TODO plan
- diri self-score runs the same DIRI scoring flow on DIRI itself
- diri compare diffs two DIRI reports to show progress over time
- diri operator-packet and install-operator expose the DIRI Operator Bridge for AI agents
- the DIRI score combines intent match, functional, behavioral, visual ux, constraint and completeness metrics
- DIRI never reports a perfect 100 score because full intent reproduction is treated as unprovable
- every DIRI report surfaces score, gaps, and next actions through a clear console and Markdown ux layout with confidence notes

Technical constraints:
- built in Python as a Typer CLI using Pydantic data models
- reports are inspectable JSON and Markdown artifacts
- deterministic rule-based MVP backed by a mock LLM provider interface

Must not become:
- a generic code quality or lint analyzer
- a tool that rewards clean architecture, test count, or short functions for their own sake
- a cross-project benchmark that compares one project's DIRI score to another project's
- a scorer that ever claims 100 percent intent reproduction
