"""Command-line entry point for the workout manager API."""

import argparse

from backend.workout_manager.api.http_server import WorkoutHTTPServer
from backend.workout_manager.application.workout_service import WorkoutService


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
) -> WorkoutHTTPServer:
    """Build the HTTP server and its application dependencies."""
    return WorkoutHTTPServer((host, port), WorkoutService())


def main() -> None:
    """Start the API using the host and port supplied on the command line."""
    parser = argparse.ArgumentParser(description="Workout manager API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    arguments = parser.parse_args()
    server = create_server(arguments.host, arguments.port)
    print(f"API available at http://{arguments.host}:{arguments.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the API.")
    finally:
        server.server_close()
