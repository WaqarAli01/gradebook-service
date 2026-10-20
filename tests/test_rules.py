from rules import ensure_weight_fits

def test_empty_existing_weights_fits() -> None:
    ensure_weight_fits([], 50.0)