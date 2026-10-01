"""Doubly linked list that manages the active workout sequence."""

from typing import List, Optional

from backend.workout_manager.domain.exercise import ExerciseNode
from backend.workout_manager.domain.exceptions import (
    EmptyWorkoutError,
    WorkoutBoundaryError,
)


class DoublyLinkedList:
    """Maintain a workout sequence with O(1) active-node operations."""

    def __init__(self) -> None:
        """Initialize an empty workout."""
        self.head: Optional[ExerciseNode] = None
        self.tail: Optional[ExerciseNode] = None
        self.current: Optional[ExerciseNode] = None
        self.total_exercises = 0

    def _require_current(self) -> ExerciseNode:
        """Return the active node or raise when the workout is empty."""
        if self.current is None:
            raise EmptyWorkoutError("The workout has no active exercise.")
        return self.current

    def advance(self) -> ExerciseNode:
        """Complete the active exercise and advance when possible."""
        current = self._require_current()
        current.completed = True
        if current.next is not None:
            self.current = current.next
        return self.current

    def go_back(self) -> ExerciseNode:
        """Move to the previous exercise, or raise at the head."""
        current = self._require_current()
        if current.previous is None:
            raise WorkoutBoundaryError("Already at the first exercise.")
        self.current = current.previous
        return self.current

    def append(self, exercise: ExerciseNode) -> None:
        """Append an exercise to the tail in O(1)."""
        if self.tail is None:
            self.head = exercise
            self.tail = exercise
            self.current = exercise
        else:
            exercise.previous = self.tail
            self.tail.next = exercise
            self.tail = exercise
        self.total_exercises += 1

    def insert_after_current(self, exercise: ExerciseNode) -> None:
        """Insert an exercise after the active node in O(1)."""
        current = self._require_current()
        following = current.next

        exercise.previous = current
        exercise.next = following
        current.next = exercise
        if following is not None:
            following.previous = exercise
        else:
            self.tail = exercise
        self.total_exercises += 1

    def skip_current(self) -> Optional[ExerciseNode]:
        """Remove the active node and select its successor or predecessor."""
        current = self._require_current()
        previous = current.previous
        following = current.next

        if previous is None:
            self.head = following
        else:
            previous.next = following

        if following is None:
            self.tail = previous
        else:
            following.previous = previous

        self.current = following if following is not None else previous
        current.previous = None
        current.next = None
        self.total_exercises -= 1

        if self.total_exercises == 0:
            self.head = None
            self.tail = None
            self.current = None
        return self.current

    def progress_percentage(self) -> float:
        """Return the percentage of exercises marked as completed."""
        if self.total_exercises == 0:
            return 0.0

        completed = 0
        node = self.head
        while node is not None:
            if node.completed:
                completed += 1
            node = node.next
        return completed / self.total_exercises * 100

    def estimated_rest_seconds(self) -> int:
        """Sum configured rest periods between sets across the workout."""
        total_seconds = 0
        node = self.head
        while node is not None:
            total_seconds += max(node.sets - 1, 0) * node.rest_seconds
            node = node.next
        return total_seconds

    def to_list(self) -> List[ExerciseNode]:
        """Return the exercises from head to tail."""
        exercises: List[ExerciseNode] = []
        node = self.head
        while node is not None:
            exercises.append(node)
            node = node.next
        return exercises
