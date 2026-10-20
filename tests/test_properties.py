from typing import Any
from unittest.mock import patch

from hypothesis import given
from hypothesis import strategies as st

import gradebook


@given(scores=st.lists(st.integers(min_value=0, max_value=20), min_size=1, max_size=5))
def test_student_percentage_never_exceeds_assessment_weight_limit(scores: list[int]) -> None:
    state: dict[str, Any] = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {"A1": {"id": "A1", "weight": 10.0, "total": 20.0}},
        "marks": [],
    }

    for score in scores:
        gradebook.add_mark(
            state,
            {"student": "S1", "assessment": "A1", "score": score},
            lambda: "2026-10-20 12:00:00",
            lambda: None,
        )

    with patch.object(gradebook, "STATE", state):
        pct_value = float(gradebook.pct("S1"))
        assert pct_value <= 10.0