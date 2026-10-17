from typing import Any

import gradebook


def test_student_without_marks_has_zero_percent(loaded: dict[str, Any]) -> None:
    assert gradebook.pct("S1") == "0"


def test_one_mark_counts_score_over_total_times_weight(loaded: dict[str, Any]) -> None:
    loaded["marks"].append({"student": "S1", "assessment": "A1", "score": 15})
    assert gradebook.pct("S1") == "7.5"


def test_mark_for_unknown_assessment_is_ignored(loaded: dict[str, Any]) -> None:
    loaded["marks"].append({"student": "S1", "assessment": "GHOST", "score": 5})
    assert gradebook.pct("S1") == "0"