from errors import ValidationError

def ensure_weight_fits(existing_weights: list[float], new_weight: float) -> None:
    total = sum(existing_weights) + new_weight
    if total - 100.0 > 1e-9:
        raise ValidationError("Total weight cannot exceed 100")