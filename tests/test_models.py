"""Unit tests for domain models and boundary parsers."""

import math
import pytest
from errors import ValidationError
from models import parse_assessment, parse_mark, parse_number, parse_student


def test_numeric_string_accepted() -> None:
    """Check that valid numeric strings are accepted as float."""
    assert parse_number("42.5", "score") == 42.5
    assert parse_number("10", "total") == 10.0


def test_text_bool_nan_rejected() -> None:
    """Check that invalid numbers, booleans, and non-finite values are rejected."""
    with pytest.raises(ValidationError):
        parse_number("invalid_number", "score")
    with pytest.raises(ValidationError):
        parse_number(True, "score")
    with pytest.raises(ValidationError):
        parse_number(math.nan, "score")
    with pytest.raises(ValidationError):
        parse_number(float("inf"), "score")


def test_zero_total_rejected() -> None:
    """Check that total cannot be zero or negative."""
    with pytest.raises(ValidationError):
        parse_assessment({"id": "A1", "title": "Midterm", "weight": 20, "total": 0})


def test_negative_score_rejected() -> None:
    """Check that negative marks are rejected."""
    with pytest.raises(ValidationError):
        parse_mark({"student": "S1", "assessment": "A1", "score": -1.0})


def test_missing_field_rejected() -> None:
    """Check that omitting any required field fails fast."""
    with pytest.raises(ValidationError):
        parse_assessment({"id": "A1", "title": "Quiz", "weight": 10})
    with pytest.raises(ValidationError):
        parse_student({"id": "S1"})


def test_payload_not_dict_rejected() -> None:
    """Check that non-dictionary JSON payloads are rejected."""
    with pytest.raises(ValidationError):
        parse_assessment(["not", "a", "dict"])
    with pytest.raises(ValidationError):
        parse_student(5)


def test_valid_assessment_parsed() -> None:
    """Check that valid assessment data creates an immutable Assessment object."""
    res = parse_assessment({"id": "A1", "title": "Final", "weight": "40", "total": "100"})
    assert res.id == "A1"
    assert res.title == "Final"
    assert res.weight == 40.0
    assert res.total == 100.0
