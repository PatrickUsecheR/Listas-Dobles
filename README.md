# Pulse Workout Manager

A full-stack workout-session manager with an **Angular frontend** and a
**Python 3.10+ backend**. The backend models the exercise sequence with a
doubly linked list and exposes it through a JSON HTTP API.

The application supports bidirectional navigation, completing or removing
the active exercise, adding exercises to the tail, and inserting exercises
after the active node. The workout is held in memory and is cleared when the
backend process stops.

## Requirements

- Python 3.10 or newer.
- Node.js 22.22.3, 24.15.0, or 26 or newer, and npm.

Angular 22 requires a supported Node.js release. The required major/minor
version is recorded in `frontend/.nvmrc`.

## Project layout

```text
.
├── backend/
│   └── workout_manager/
│       ├── api/
│       │   └── http_server.py          HTTP routes, JSON, and CORS
│       ├── application/
│       │   └── workout_service.py      Validation and application use cases
│       ├── domain/
│       │   ├── doubly_linked_list.py   Workout navigation and list operations
│       │   ├── exercise.py             Exercise node dataclass
│       │   └── exceptions.py           Domain-specific errors
│       ├── __main__.py                 Python module entry point
│       └── main.py                     Server construction and CLI
├── frontend/
│   ├── src/app/
│   │   ├── app.component.*             Workout screen and presentation
│   │   ├── workout-api.service.ts      Typed HTTP client
│   │   └── workout.model.ts            Frontend/API data contracts
│   ├── package.json
│   └── angular.json
├── tests/
│   ├── integration/                    HTTP and application-service tests
│   └── unit/                           Doubly linked list tests
├── .gitignore
└── README.md
```

### Backend responsibilities

- **Domain:** `ExerciseNode` stores exercise data and neighboring links.
  `DoublyLinkedList` owns the head, tail, active exercise, count, navigation,
  insertion, deletion, progress, and rest-time calculations.
- **Application:** `WorkoutService` validates input, coordinates domain
  operations, and serializes state for the API.
- **API:** `WorkoutHTTPServer` maps HTTP requests and domain errors to JSON
  responses. It uses only the Python standard library.
- **Entry point:** `python -m backend.workout_manager` starts the API.

Navigation, insertion after the current exercise, and removal of the current
exercise are O(1). Progress and rest-time summaries traverse the list and are
O(n).

### Frontend responsibilities

The standalone Angular component renders the session and validates the
exercise form. `WorkoutApiService` owns HTTP requests and API error messages;
`workout.model.ts` describes the API payloads and workout state.

## Run the application

Open two terminals in the repository root.

Start the backend in the first terminal:

```powershell
py -m backend.workout_manager
```

The API listens on `http://localhost:8000`.

Install dependencies and start Angular in the second terminal:

```powershell
Set-Location frontend
npm install
npm start
```

Open `http://localhost:4200`. Keep both processes running while using the
application.

## HTTP API

All endpoints use the `/api/workout` base path and JSON:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/workout` | Return exercises, active exercise, and metrics |
| `POST` | `/api/workout` | Append an exercise |
| `POST` | `/api/workout/insert` | Insert an exercise after the active exercise |
| `POST` | `/api/workout/advance` | Complete the active exercise and advance |
| `POST` | `/api/workout/back` | Move to the previous exercise |
| `POST` | `/api/workout/skip` | Remove the active exercise |

Exercise request fields are `name`, `sets`, `reps`, `weight_kg`, and
`rest_seconds`. Invalid input returns `400`; an empty workout or navigation
beyond a boundary returns `409`.

Estimated rest time sums `sets - 1` rest periods for each exercise. The
application does not estimate the time required to perform repetitions.

## Run tests and build

Run backend unit and HTTP integration tests from the repository root:

```powershell
py -m unittest discover -s tests -v
```

Build and test the Angular frontend:

```powershell
Set-Location frontend
npm run build
npm test -- --no-watch --browsers=ChromeHeadless
npm audit
```
