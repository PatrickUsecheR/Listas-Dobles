"""Application service for validating and managing workout operations."""

from math import isfinite
from threading import RLock
from typing import Any, Dict, Optional

from backend.workout_manager.domain.doubly_linked_list import DoublyLinkedList
from backend.workout_manager.domain.exercise import ExerciseNode


class WorkoutService:
    """Coordinate workout use cases and expose JSON-compatible state."""

    def __init__(self, workout: Optional[DoublyLinkedList] = None) -> None:
        """Create a service around a new or supplied workout list."""
        self._workout = workout if workout is not None else DoublyLinkedList()
        self._lock = RLock()

    @staticmethod
    def _validate_exercise(data: Dict[str, Any]) -> ExerciseNode:
        """Validate an exercise payload and construct its domain entity."""
        name = data.get("name")
        sets = data.get("sets")
        reps = data.get("reps")
        weight_kg = data.get("weight_kg")
        rest_seconds = data.get("rest_seconds")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Exercise name is required.")
        if isinstance(sets, bool) or not isinstance(sets, int) or sets < 1:
            raise ValueError("Sets must be a positive integer.")
        if isinstance(reps, bool) or not isinstance(reps, int) or reps < 1:
            raise ValueError("Repetitions must be a positive integer.")
        if (
            isinstance(weight_kg, bool)
            or not isinstance(weight_kg, (int, float))
            or weight_kg < 0
        ):
            raise ValueError("Weight must be a finite, non-negative number.")
        try:
            validated_weight = float(weight_kg)
        except OverflowError as error:
            raise ValueError(
                "Weight is outside the supported range."
            ) from error
        if not isfinite(validated_weight):
            raise ValueError("Weight must be a finite, non-negative number.")
        if (
            isinstance(rest_seconds, bool)
            or not isinstance(rest_seconds, int)
            or rest_seconds < 0
        ):
            raise ValueError("Rest time must be a non-negative integer.")

        return ExerciseNode(
            name=name.strip(),
            sets=sets,
            reps=reps,
            weight_kg=validated_weight,
            rest_seconds=rest_seconds,
        )

    @staticmethod
    def _serialize_exercise(exercise: ExerciseNode) -> Dict[str, Any]:
        """Convert an exercise entity to the public JSON representation."""
        return {
            "id": exercise.exercise_id,
            "name": exercise.name,
            "sets": exercise.sets,
            "reps": exercise.reps,
            "weight_kg": exercise.weight_kg,
            "rest_seconds": exercise.rest_seconds,
            "completed": exercise.completed,
        }

    def get_state(self) -> Dict[str, Any]:
        """Return exercises, active exercise, and workout metrics."""
        with self._lock:
            exercises = [
                self._serialize_exercise(exercise)
                for exercise in self._workout.to_list()
            ]
            current = self._workout.current
            return {
                "exercises": exercises,
                "current": (
                    self._serialize_exercise(current)
                    if current is not None
                    else None
                ),
                "total_exercises": self._workout.total_exercises,
                "progress": self._workout.progress_percentage(),
                "estimated_rest_seconds": (
                    self._workout.estimated_rest_seconds()
                ),
            }

    def append_exercise(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and append an exercise to the workout."""
        exercise = self._validate_exercise(data)
        with self._lock:
            self._workout.append(exercise)
            return self.get_state()

    def insert_after_current(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and insert an exercise after the active exercise."""
        exercise = self._validate_exercise(data)
        with self._lock:
            self._workout.insert_after_current(exercise)
            return self.get_state()

    def advance(self) -> Dict[str, Any]:
        """Complete the active exercise and advance to the next one."""
        with self._lock:
            self._workout.advance()
            return self.get_state()

    def go_back(self) -> Dict[str, Any]:
        """Move the active exercise to its predecessor."""
        with self._lock:
            self._workout.go_back()
            return self.get_state()

    def skip_current(self) -> Dict[str, Any]:
        """Remove the active exercise from the workout."""
        with self._lock:
            self._workout.skip_current()
            return self.get_state()
