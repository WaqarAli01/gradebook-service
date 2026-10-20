"""Business rule validation functions for gradebook service."""

from errors import ValidationError

MAX_TOTAL_WEIGHT = 100.0
TOLERANCE = 1e-9


def ensure_weight_fits(existing_weights: list[float], new_weight: float) -> None:
    """Ensure adding new_weight to existing_weights does not exceed MAX_TOTAL_WEIGHT."""
    total = sum(existing_weights) + new_weight
    if total - MAX_TOTAL_WEIGHT > TOLERANCE:
        raise ValidationError(f"Total weight cannot exceed {MAX_TOTAL_WEIGHT}")