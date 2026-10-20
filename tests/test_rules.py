import pytest
from errors import ValidationError
from rules import ensure_weight_fits

def test_empty_existing_weights_fits() -> None:
    ensure_weight_fits([], 50.0)

def test_weight_exceeding_100_raises_validation_error() -> None:
    with pytest.raises(ValidationError, match="100"):
        ensure_weight_fits([60.0], 50.0)