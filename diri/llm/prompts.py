INTENT_DISCOVERY_PROMPT = """You are DIRI, a Developer Intent Reproduction Index system.

Your job is not to evaluate generic code quality.
Your job is to understand what result the developer truly wanted.

Return strict JSON matching DeveloperIntent.
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
