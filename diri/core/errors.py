class DiriError(Exception):
    """Base exception for user-facing DIRI failures."""


class WorkspaceMissingError(DiriError):
    """Raised when a command needs an initialized .diri workspace."""
