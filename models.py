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


def parse_number(raw: object, field: str) -> float:
    """Parse a number, accepting float, int, or numeric strings while rejecting bool, nan, and inf."""
    if isinstance(raw, bool) or raw is None:
        raise ValidationError(f"Field '{field}' must be a number, not boolean or null")
    if isinstance(raw, (int, float)):
        val = float(raw)
    elif isinstance(raw, str):
        try:
            val = float(raw.strip())
        except ValueError:
            raise ValidationError(f"Field '{field}' must be a valid numeric string") from None
    else:
        raise ValidationError(f"Field '{field}' must be a numeric value")

    if not math.isfinite(val):
        raise ValidationError(f"Field '{field}' must be a finite number")
    return val


def parse_text(raw: object, field: str) -> str:
    """Parse and trim a non-blank string."""
    if not isinstance(raw, str):
        raise ValidationError(f"Field '{field}' must be a string")
    cleaned = raw.strip()
    if not cleaned:
        raise ValidationError(f"Field '{field}' cannot be empty")
    return cleaned


def _ensure_dict(payload: object) -> Mapping[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    return payload


def parse_student(payload: object) -> Student:
    """Parse and validate student dictionary."""
    data = _ensure_dict(payload)
    if "id" not in data:
        raise ValidationError("Field 'id' is required")
    if "name" not in data:
        raise ValidationError("Field 'name' is required")
    return Student(
        id=parse_text(data["id"], "id"),
        name=parse_text(data["name"], "name"),
    )


def parse_assessment(payload: object) -> Assessment:
    """Parse and validate assessment dictionary."""
    data = _ensure_dict(payload)
    for key in ("id", "title", "weight", "total"):
        if key not in data:
            raise ValidationError(f"Field '{key}' is required")
    return Assessment(
        id=parse_text(data["id"], "id"),
        title=parse_text(data["title"], "title"),
        weight=parse_number(data["weight"], "weight"),
        total=parse_number(data["total"], "total"),
    )


def parse_mark(payload: object) -> Mark:
    """Parse and validate mark dictionary."""
    data = _ensure_dict(payload)
    for key in ("student", "assessment", "score"):
        if key not in data:
            raise ValidationError(f"Field '{key}' is required")
    return Mark(
        student=parse_text(data["student"], "student"),
        assessment=parse_text(data["assessment"], "assessment"),
        score=parse_number(data["score"], "score"),
    )