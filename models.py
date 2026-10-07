"""Domain data models and parsers."""

from dataclasses import dataclass
import math
from typing import Any, Mapping
from errors import ValidationError


@dataclass(frozen=True)
class Student:
    """Immutable student record."""
    id: str
    name: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValidationError("Field 'id' cannot be empty")
        if not self.name:
            raise ValidationError("Field 'name' cannot be empty")


@dataclass(frozen=True)
class Assessment:
    """Immutable assessment record."""
    id: str
    title: str
    weight: float
    total: float

    def __post_init__(self) -> None:
        if not self.id:
            raise ValidationError("Field 'id' cannot be empty")
        if not self.title:
            raise ValidationError("Field 'title' cannot be empty")
        if not (0.0 <= self.weight <= 100.0):
            raise ValidationError("Field 'weight' must be between 0 and 100")
        if self.total <= 0.0:
            raise ValidationError("Field 'total' must be strictly greater than 0")


@dataclass(frozen=True)
class Mark:
    """Immutable mark record."""
    student: str
    assessment: str
    score: float

    def __post_init__(self) -> None:
        if not self.student:
            raise ValidationError("Field 'student' cannot be empty")
        if not self.assessment:
            raise ValidationError("Field 'assessment' cannot be empty")
        if self.score < 0.0:
            raise ValidationError("Field 'score' cannot be negative")