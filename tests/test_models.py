from typing import Any

import pytest

import models
from errors import ValidationError


@pytest.mark.parametrize(
    "val",
    [
        pytest.param("15", id="string-int"),
        pytest.param(15, id="int"),
        pytest.param("2.5", id="string-float"),
    ],
)
def test_valid_numbers_parsed_correctly(val: Any) -> None:
    assert models.parse_number(val, "score") is not None


@pytest.mark.parametrize(
    "val",
    [
        pytest.param("abc", id="string-letters"),
        pytest.param(True, id="bool"),
        pytest.param(None, id="none"),
        pytest.param([], id="list"),
        pytest.param("nan", id="nan-string"),
        pytest.param("inf", id="inf-string"),
    ],
)
def test_invalid_numbers_raise_validation_error(val: Any) -> None:
    with pytest.raises(ValidationError):
        models.parse_number(val, "score")