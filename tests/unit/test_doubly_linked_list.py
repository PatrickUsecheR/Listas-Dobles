"""Unit tests for the workout doubly linked list."""

import unittest
from typing import Optional

from backend.workout_manager.domain.doubly_linked_list import DoublyLinkedList
from backend.workout_manager.domain.exercise import ExerciseNode
from backend.workout_manager.domain.exceptions import (
    EmptyWorkoutError,
    WorkoutBoundaryError,
)


def make_exercise(name: str) -> ExerciseNode:
    """Create a test exercise with standard training values."""
    return ExerciseNode(
        name=name,
        sets=3,
        reps=10,
        weight_kg=20.0,
        rest_seconds=60,
        exercise_id=name.lower(),
    )


class DoublyLinkedListTests(unittest.TestCase):
    """Verify navigation, editing, and workout metrics."""

    def test_navigation_and_boundaries(self) -> None:
        workout = DoublyLinkedList()
        workout.append(make_exercise("Squats"))
        workout.append(make_exercise("Deadlift"))

        self.assertEqual(workout.advance().name, "Deadlift")
        self.assertTrue(workout.head.completed)
        self.assertEqual(workout.advance().name, "Deadlift")
        self.assertEqual(workout.go_back().name, "Squats")
        with self.assertRaises(WorkoutBoundaryError):
            workout.go_back()
        self.assertEqual(workout.current.name, "Squats")

    def test_insert_after_current_and_preserve_links(self) -> None:
        workout = DoublyLinkedList()
        workout.append(make_exercise("Squats"))
        workout.append(make_exercise("Deadlift"))
        workout.insert_after_current(make_exercise("Lunges"))

        self.assertEqual(
            [exercise.name for exercise in workout.to_list()],
            ["Squats", "Lunges", "Deadlift"],
        )
        self.assertIs(workout.head.next.previous, workout.head)
        self.assertIs(workout.tail.previous.next, workout.tail)
        self.assertEqual(workout.total_exercises, 3)

    def test_skip_head_tail_and_only_node(self) -> None:
        workout = DoublyLinkedList()
        workout.append(make_exercise("Squats"))
        workout.append(make_exercise("Lunges"))
        workout.skip_current()
        self.assertEqual(workout.head.name, "Lunges")
        self.assertIsNone(workout.head.previous)
        workout.skip_current()
        self.assertEqual(workout.total_exercises, 0)
        self.assertIsNone(workout.head)
        self.assertIsNone(workout.tail)
        self.assertIsNone(workout.current)

        workout.append(make_exercise("Deadlift"))
        workout.advance()
        workout.skip_current()
        self.assertIsNone(workout.head)
        self.assertIsNone(workout.tail)
        self.assertIsNone(workout.current)

    def test_empty_workout_and_metrics(self) -> None:
        workout = DoublyLinkedList()
        self.assertEqual(workout.progress_percentage(), 0.0)
        self.assertEqual(workout.estimated_rest_seconds(), 0)
        with self.assertRaises(EmptyWorkoutError):
            workout.advance()
        with self.assertRaises(EmptyWorkoutError):
            workout.go_back()
        with self.assertRaises(EmptyWorkoutError):
            workout.skip_current()

        workout.append(make_exercise("Squats"))
        workout.append(make_exercise("Deadlift"))
        workout.advance()
        self.assertEqual(workout.progress_percentage(), 50.0)
        self.assertEqual(workout.estimated_rest_seconds(), 240)

    def test_skip_tail_selects_predecessor(self) -> None:
        workout = DoublyLinkedList()
        workout.append(make_exercise("Squats"))
        workout.append(make_exercise("Deadlift"))
        workout.advance()

        current: Optional[ExerciseNode] = workout.skip_current()

        self.assertEqual(current.name, "Squats")
        self.assertIs(workout.tail, current)
        self.assertIsNone(workout.tail.next)


if __name__ == "__main__":
    unittest.main()
