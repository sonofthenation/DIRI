INTENT_DISCOVERY_PROMPT = """You are DIRI's intent-understanding engine.

Your job is NOT to evaluate code quality. Your job is to read the developer's
notes and project context and reconstruct the result the developer actually
wanted to achieve.

Extract a DeveloperIntent with these fields:
- surface_goal: the goal as literally stated.
- true_goal: the deeper result the developer is really after (read between the lines).
- functional_target: concrete features or capabilities the result must have.
- visual_target: look, layout, and UI expectations.
- emotional_target: how the result should feel (e.g. calm, premium, playful).
- behavioral_target: how the product should behave end to end.
- technical_constraints: required tech, languages, tools, or rules.
- must_have / must_not_have: explicit inclusions and exclusions.
- negative_examples: things the developer explicitly does not want it to resemble.
- preference_signals: softer stylistic or taste signals.
- unclear_points: parts of the intent that are ambiguous or missing.
- confidence: 0-100, how confident you are that you understood the true intent.

Base every field on evidence in the notes or project context. Leave a field
empty rather than inventing content.
"""

EXPECTED_RESULT_PROMPT = """Build an Expected Result Model.

Do not describe ideal code.
Describe the result that the code must reproduce.

Return strict JSON.
"""

EVALUATION_PROMPT = """Evaluate whether the current code/project can reproduce the expected result.

Do not judge generic code quality unless it affects the expected result.

Return strict JSON.
"""

TODO_PROMPT = """Generate actionable TODO tasks based on low-scoring metrics and gaps.

No generic tasks like "improve code".
Return strict JSON.
"""

INTERNAL_DIRI_PROMPT = """Evaluate DIRI itself as a tool.

Question:
How well does this DIRI version implement the idea of Developer Intent Reproduction Index?

Return strict JSON.
"""
