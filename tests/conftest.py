from typing import Any

import pytest

import gradebook


@pytest.fixture
def state() -> dict[str, Any]:
    return {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {
            "A1": {"id": "A1", "weight": 10.0, "total": 20.0},
            "A2": {"id": "A2", "weight": 30.0, "total": 50.0},
        },
        "marks": [],
    }


@pytest.fixture
def loaded(monkeypatch: pytest.MonkeyPatch, state: dict[str, Any]) -> dict[str, Any]:
    monkeypatch.setattr(gradebook, "STATE", state)
    return state