"""Workout exercise entity and doubly linked-list node."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class ExerciseNode:
    """An exercise and its links to neighboring nodes in a workout."""

    name: str
    sets: int
    reps: int
    weight_kg: float
    rest_seconds: int
    exercise_id: str = field(default_factory=lambda: str(uuid4()))
    completed: bool = False
    previous: Optional["ExerciseNode"] = None
    next: Optional["ExerciseNode"] = None
