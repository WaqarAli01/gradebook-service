import json
from pathlib import Path
from typing import Any

import pytest

import gradebook


@pytest.fixture
def temp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    file_path = tmp_path / "gradebook.json"
    monkeypatch.setattr(gradebook, "DATA", file_path)
    return file_path


def test_saved_gradebook_loads_back_unchanged(
    temp_storage: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data: dict[str, Any] = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {},
        "marks": [],
    }
    monkeypatch.setattr(gradebook, "STATE", data)
    gradebook.save()

    # Reset STATE to an empty dict to ensure load() actually reads from disk
    monkeypatch.setattr(gradebook, "STATE", {})
    gradebook.load()

    assert gradebook.STATE == data


def test_load_when_file_does_not_exist_returns_empty_structure(
    temp_storage: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert not temp_storage.exists()

    monkeypatch.setattr(gradebook, "STATE", {})
    gradebook.load()

    assert gradebook.STATE == {"students": {}, "assessments": {}, "marks": []}


def test_load_corrupted_file_raises_json_decode_error(temp_storage: Path) -> None:
    temp_storage.write_text("{corrupted json")
    with pytest.raises(json.JSONDecodeError):
        gradebook.load()