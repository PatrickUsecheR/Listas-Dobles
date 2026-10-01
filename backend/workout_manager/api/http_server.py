"""JSON HTTP adapter for workout application use cases."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, cast
from urllib.parse import urlparse

from backend.workout_manager.application.workout_service import WorkoutService
from backend.workout_manager.domain.exceptions import (
    EmptyWorkoutError,
    WorkoutBoundaryError,
)


class WorkoutHTTPServer(ThreadingHTTPServer):
    """HTTP server that shares a workout service across requests."""

    def __init__(
        self,
        address: tuple[str, int],
        service: WorkoutService,
    ) -> None:
        """Initialize the server with its application service."""
        self.service = service
        super().__init__(address, WorkoutRequestHandler)


class WorkoutRequestHandler(BaseHTTPRequestHandler):
    """Map REST requests to workout service operations."""

    server: WorkoutHTTPServer
    server_version = "WorkoutHTTP/1.0"

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests from the Angular server."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self._add_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        """Return the current workout state."""
        if urlparse(self.path).path != "/api/workout":
            self._respond(
                {"error": "Route not found."},
                HTTPStatus.NOT_FOUND,
            )
            return
        self._respond(self.server.service.get_state())

    def do_POST(self) -> None:
        """Execute a workout operation received in a POST request."""
        try:
            data = self._read_json()
            route = urlparse(self.path).path
            service = self.server.service

            if route == "/api/workout":
                state = service.append_exercise(data)
                status = HTTPStatus.CREATED
            elif route == "/api/workout/insert":
                state = service.insert_after_current(data)
                status = HTTPStatus.CREATED
            elif route == "/api/workout/advance":
                state = service.advance()
                status = HTTPStatus.OK
            elif route == "/api/workout/back":
                state = service.go_back()
                status = HTTPStatus.OK
            elif route == "/api/workout/skip":
                state = service.skip_current()
                status = HTTPStatus.OK
            else:
                self._respond(
                    {"error": "Route not found."},
                    HTTPStatus.NOT_FOUND,
                )
                return
            self._respond(state, status)
        except (ValueError, UnicodeDecodeError) as error:
            self._respond({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except (EmptyWorkoutError, WorkoutBoundaryError) as error:
            self._respond({"error": str(error)}, HTTPStatus.CONFLICT)

    def _read_json(self) -> Dict[str, Any]:
        """Read and validate a JSON object from the request body."""
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Content-Length must be an integer.") from error
        if content_length < 1 or content_length > 1_000_000:
            raise ValueError(
                "Request body must be between 1 and 1,000,000 bytes."
            )

        content = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON request body must be an object.")
        return cast(Dict[str, Any], data)

    def _respond(
        self,
        data: Dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        """Send a JSON response with CORS headers."""
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._add_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _add_cors_headers(self) -> None:
        """Allow requests from the local Angular development server."""
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:4200",
        )
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
