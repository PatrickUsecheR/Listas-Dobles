"""Domain-specific errors raised by workout operations."""


class EmptyWorkoutError(Exception):
    """Raised when an operation requires an active exercise."""


class WorkoutBoundaryError(Exception):
    """Raised when navigation cannot move beyond a workout boundary."""
