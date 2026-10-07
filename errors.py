"""Domain error hierarchy for gradebook service."""

class GradebookError(Exception):
    """Base class for all domain errors."""


class ValidationError(GradebookError):
    """Raised when user input violates validation rules."""


class NotFoundError(GradebookError):
    """Raised when an entity or resource is not found."""


class ConflictError(GradebookError):
    """Raised when an identifier already exists."""
