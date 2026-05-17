DEFAULT_WORKSPACE_DIR = ".diri"

DEFAULT_WEIGHTS = {
    "intent_match": 0.25,
    "functional_reproduction": 0.20,
    "behavioral_reproduction": 0.15,
    "visual_ux_reproduction": 0.20,
    "constraint_respect": 0.10,
    "completeness": 0.10,
}

METRIC_LABELS = {
    "intent_match": "Intent Match",
    "functional_reproduction": "Functional Reproduction",
    "behavioral_reproduction": "Behavioral Reproduction",
    "visual_ux_reproduction": "Visual/UX Reproduction",
    "constraint_respect": "Constraint Respect",
    "completeness": "Completeness",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".cache",
    ".uv-cache",
    ".pytest_cache",
    ".pytest-tmp",
}
