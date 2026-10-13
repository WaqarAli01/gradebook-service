
import pytest
import gradebook


def test_student_without_marks_has_zero_percent(monkeypatch: pytest.MonkeyPatch) -> None:
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "weight": 10.0, "total": 20.0}},
        "marks": [],
    }

    monkeypatch.setattr(gradebook, "STATE", state)

    assert gradebook.pct("S1") == "0"


def test_one_mark_counts_score_over_total_times_weight(monkeypatch: pytest.MonkeyPatch) -> None:
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "weight": 10.0, "total": 20.0}},
        "marks": [{"student": "S1", "assessment": "A1", "score": 15}],
    }

    monkeypatch.setattr(gradebook, "STATE", state)

    assert gradebook.pct("S1") == "7.5"


def test_mark_for_unknown_assessment_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "weight": 10.0, "total": 20.0}},
        "marks": [{"student": "S1", "assessment": "GHOST", "score": 5}],
    }

    monkeypatch.setattr(gradebook, "STATE", state)

    assert gradebook.pct("S1") == "0"
