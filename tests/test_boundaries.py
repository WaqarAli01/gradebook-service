from typing import Any
from unittest.mock import Mock

import pytest

import gradebook
from errors import ValidationError


@pytest.mark.parametrize(
    ("weight", "should_pass"),
    [
        pytest.param(0.0, True, id="weight-boundary-0"),
        pytest.param(100.0, True, id="weight-boundary-100"),
        pytest.param(-0.01, False, id="weight-boundary-negative"),
        pytest.param(100.01, False, id="weight-boundary-above-100"),
    ],
)
def test_assessment_weight_boundaries(weight: float, should_pass: bool) -> None:
    assessment_payload = {"id": "B1", "title": "Boundary Test", "weight": weight, "total": 100.0}
    if should_pass:
        gradebook.add_assessment({}, assessment_payload, Mock())
    else:
        with pytest.raises(ValidationError):
            gradebook.add_assessment({}, assessment_payload, Mock())


@pytest.mark.parametrize(
    ("total", "should_pass"),
    [
        pytest.param(0.01, True, id="total-boundary-0.01"),
        pytest.param(0.0, False, id="total-boundary-0"),
    ],
)
def test_assessment_total_boundaries(total: float, should_pass: bool) -> None:
    assessment_payload = {"id": "B2", "title": "Total Test", "weight": 10.0, "total": total}
    if should_pass:
        gradebook.add_assessment({}, assessment_payload, Mock())
    else:
        with pytest.raises(ValidationError):
            gradebook.add_assessment({}, assessment_payload, Mock())


@pytest.mark.parametrize(
    ("score", "should_pass"),
    [
        pytest.param(0.0, True, id="score-boundary-0"),
        pytest.param(20.0, True, id="score-boundary-20"),
        pytest.param(-0.01, False, id="score-boundary-negative"),
        pytest.param(20.01, False, id="score-boundary-above-total"),
    ],
)
def test_add_mark_score_boundaries(state: dict[str, Any], score: float, should_pass: bool) -> None:
    save_mock = Mock()
    mark = {"student": "S1", "assessment": "A1", "score": score}

    if should_pass:
        gradebook.add_mark(state, mark, lambda: "2026-10-20 12:00:00", save_mock)
    else:
        with pytest.raises(ValidationError):
            gradebook.add_mark(state, mark, lambda: "2026-10-20 12:00:00", save_mock)
        assert len(state["marks"]) == 0