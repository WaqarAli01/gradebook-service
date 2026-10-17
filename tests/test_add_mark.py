from typing import Any
from unittest.mock import Mock

import pytest

import gradebook
from errors import NotFoundError, ValidationError


def stub_clock() -> str:
    return "2026-10-12 09:00:00"


def test_valid_mark_stored_with_expected_dict_and_timestamp(state: dict[str, Any]) -> None:
    save_mock = Mock()
    mark = {"student": "S1", "assessment": "A1", "score": 15}

    gradebook.add_mark(state, mark, stub_clock, save_mock)

    assert len(state["marks"]) == 1
    assert state["marks"][0] == {
        "student": "S1",
        "assessment": "A1",
        "score": 15,
        "at": "2026-10-12 09:00:00",
    }


def test_valid_mark_calls_save_exactly_once(state: dict[str, Any]) -> None:
    save_mock = Mock()
    mark = {"student": "S1", "assessment": "A1", "score": 15}

    gradebook.add_mark(state, mark, stub_clock, save_mock)

    save_mock.assert_called_once_with()


@pytest.mark.parametrize(
    ("mark", "expected_exception"),
    [
        pytest.param(
            {"student": "S99", "assessment": "A1", "score": 10},
            NotFoundError,
            id="unknown-student",
        ),
        pytest.param(
            {"student": "S1", "assessment": "A99", "score": 10},
            NotFoundError,
            id="unknown-assessment",
        ),
        pytest.param(
            {"student": "S1", "assessment": "A1", "score": 25},
            ValidationError,
            id="score-above-total",
        ),
    ],
)
def test_invalid_marks_raise_exceptions_and_do_not_modify_state_or_call_save(
    state: dict[str, Any], mark: dict[str, Any], expected_exception: Any
) -> None:
    save_mock = Mock()

    with pytest.raises(expected_exception):
        gradebook.add_mark(state, mark, stub_clock, save_mock)

    assert state["marks"] == []
    save_mock.assert_not_called()