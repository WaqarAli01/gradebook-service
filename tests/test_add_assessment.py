from typing import Any
from unittest.mock import Mock
import pytest
import gradebook
from errors import ConflictError, ValidationError


def test_valid_assessment_stored_and_saved_once(state: dict[str, Any]) -> None:
    save_mock = Mock()
    assessment = {"id": "A3", "title": "Exam", "weight": 40.0, "total": 100.0}

    gradebook.add_assessment(state, assessment, save_mock)

    assert "A3" in state["assessments"]
    assert state["assessments"]["A3"] == assessment
    save_mock.assert_called_once_with()


def test_assessment_exceeding_weight_limit_raises_error_and_does_not_save(
    state: dict[str, Any]
) -> None:
    save_mock = Mock()
    # state from conftest has A1 (10) and A2 (30); total existing = 40
    assessment = {"id": "A3", "title": "Exam", "weight": 70.0, "total": 100.0}

    with pytest.raises(ValidationError):
        gradebook.add_assessment(state, assessment, save_mock)

    assert "A3" not in state["assessments"]
    save_mock.assert_not_called()


def test_duplicate_assessment_id_raises_conflict_error_and_does_not_save(
    state: dict[str, Any]
) -> None:
    save_mock = Mock()
    assessment = {"id": "A1", "title": "Duplicate", "weight": 10.0, "total": 20.0}

    with pytest.raises(ConflictError):
        gradebook.add_assessment(state, assessment, save_mock)

    save_mock.assert_not_called()