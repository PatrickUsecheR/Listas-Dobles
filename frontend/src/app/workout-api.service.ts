import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ExerciseInput, WorkoutState } from './workout.model';

/** Typed HTTP client for the Python workout API. */
@Injectable({ providedIn: 'root' })
export class WorkoutApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/workout';

  getState(): Observable<WorkoutState> {
    return this.http.get<WorkoutState>(this.apiUrl);
  }

  appendExercise(exercise: ExerciseInput): Observable<WorkoutState> {
    return this.http.post<WorkoutState>(this.apiUrl, exercise);
  }

  insertAfterCurrent(exercise: ExerciseInput): Observable<WorkoutState> {
    return this.http.post<WorkoutState>(`${this.apiUrl}/insert`, exercise);
  }

  advance(): Observable<WorkoutState> {
    return this.http.post<WorkoutState>(`${this.apiUrl}/advance`, {});
  }

  goBack(): Observable<WorkoutState> {
    return this.http.post<WorkoutState>(`${this.apiUrl}/back`, {});
  }

  skipCurrent(): Observable<WorkoutState> {
    return this.http.post<WorkoutState>(`${this.apiUrl}/skip`, {});
  }

  getErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const message = error.error?.error;
      if (typeof message === 'string') {
        return message;
      }
      if (error.status === 0) {
        return 'Could not connect to the API. Make sure the backend is running.';
      }
      return `The API returned an error (${error.status}).`;
    }
    return 'An unexpected error occurred.';
  }
}
