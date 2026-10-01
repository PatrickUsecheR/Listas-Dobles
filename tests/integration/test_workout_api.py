"""Integration tests for the workout service and HTTP API."""

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.workout_manager.api.http_server import WorkoutHTTPServer
from backend.workout_manager.application.workout_service import WorkoutService


class WorkoutServiceTests(unittest.TestCase):
    """Verify service-level validation and use cases."""

    def setUp(self) -> None:
        self.service = WorkoutService()
        self.exercise = {
            "name": "Squats",
            "sets": 3,
            "reps": 10,
            "weight_kg": 25,
            "rest_seconds": 60,
        }

    def test_validation_and_mutations(self) -> None:
        with self.assertRaisesRegex(ValueError, "name"):
            self.service.append_exercise({**self.exercise, "name": " "})
        with self.assertRaisesRegex(ValueError, "finite"):
            self.service.append_exercise(
                {**self.exercise, "weight_kg": float("nan")}
            )
        with self.assertRaisesRegex(ValueError, "range"):
            self.service.append_exercise(
                {**self.exercise, "weight_kg": 10**1000}
            )

        self.service.append_exercise(self.exercise)
        self.service.insert_after_current(
            {**self.exercise, "name": "Leg press"}
        )
        state = self.service.get_state()

        self.assertEqual(state["total_exercises"], 2)
        self.assertEqual(state["current"]["name"], "Squats")
        self.assertEqual(
            [exercise["name"] for exercise in state["exercises"]],
            ["Squats", "Leg press"],
        )


class WorkoutHTTPTests(unittest.TestCase):
    """Test the HTTP contract using a temporary local server."""

    def setUp(self) -> None:
        self.server = WorkoutHTTPServer(("127.0.0.1", 0), WorkoutService())
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def post_json(self, route: str, data: dict) -> tuple[int, dict]:
        request = Request(
            self.url + route,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            response = urlopen(request)
        except HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))
        with response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_add_navigation_and_controlled_errors(self) -> None:
        exercise = {
            "name": "Deadlift",
            "sets": 4,
            "reps": 8,
            "weight_kg": 50,
            "rest_seconds": 90,
        }
        status, created = self.post_json("/api/workout", exercise)
        self.assertEqual(status, 201)
        self.assertEqual(created["current"]["name"], "Deadlift")

        status, error = self.post_json("/api/workout/back", {})
        self.assertEqual(status, 409)
        self.assertIn("first exercise", error["error"])

        with urlopen(self.url + "/api/workout") as response:
            state = json.loads(response.read().decode("utf-8"))
            self.assertEqual(
                response.headers["Access-Control-Allow-Origin"],
                "http://localhost:4200",
            )
        self.assertEqual(state["total_exercises"], 1)


if __name__ == "__main__":
    unittest.main()
