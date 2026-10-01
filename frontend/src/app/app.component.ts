import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Observable } from 'rxjs';
import { ExerciseInput, WorkoutState } from './workout.model';
import { WorkoutApiService } from './workout-api.service';

/** Main screen for managing a live workout session. */
@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  private readonly workoutApi = inject(WorkoutApiService);
  private readonly changeDetector = inject(ChangeDetectorRef);

  readonly exerciseForm = new FormGroup({
    name: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(80)],
    }),
    sets: new FormControl(3, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
    reps: new FormControl(10, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
    weightKg: new FormControl(0, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(0)],
    }),
    restSeconds: new FormControl(60, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(0)],
    }),
  });

  state: WorkoutState = {
    exercises: [],
    current: null,
    total_exercises: 0,
    progress: 0,
    estimated_rest_seconds: 0,
  };
  insertAfterCurrent = false;
  isLoading = false;
  errorMessage = '';

  get completedExercises(): number {
    return this.state.exercises.filter((exercise) => exercise.completed).length;
  }

  get canGoBack(): boolean {
    return (
      this.state.current !== null &&
      this.state.current.id !== this.state.exercises[0]?.id
    );
  }

  get isWorkoutComplete(): boolean {
    return (
      this.state.total_exercises > 0 &&
      this.completedExercises === this.state.total_exercises
    );
  }

  ngOnInit(): void {
    this.loadState();
  }

  loadState(): void {
    this.execute(this.workoutApi.getState());
  }

  advance(): void {
    this.execute(this.workoutApi.advance());
  }

  goBack(): void {
    this.execute(this.workoutApi.goBack());
  }

  skipCurrent(): void {
    this.execute(this.workoutApi.skipCurrent());
  }

  saveExercise(): void {
    if (this.exerciseForm.invalid) {
      this.exerciseForm.markAllAsTouched();
      return;
    }

    const formValue = this.exerciseForm.getRawValue();
    const exercise: ExerciseInput = {
      name: formValue.name,
      sets: formValue.sets,
      reps: formValue.reps,
      weight_kg: formValue.weightKg,
      rest_seconds: formValue.restSeconds,
    };
    const request = this.insertAfterCurrent
      ? this.workoutApi.insertAfterCurrent(exercise)
      : this.workoutApi.appendExercise(exercise);

    this.execute(request, () => {
      this.exerciseForm.reset({
        name: '',
        sets: 3,
        reps: 10,
        weightKg: 0,
        restSeconds: 60,
      });
    });
  }

  exercisePosition(exerciseId: string): number {
    return this.state.exercises.findIndex(
      (exercise) => exercise.id === exerciseId,
    ) + 1;
  }

  private execute(
    request: Observable<WorkoutState>,
    onComplete?: () => void,
  ): void {
    this.isLoading = true;
    this.errorMessage = '';
    request.subscribe({
      next: (state) => {
        this.state = state;
        this.isLoading = false;
        onComplete?.();
        this.changeDetector.markForCheck();
      },
      error: (error: unknown) => {
        this.errorMessage = this.workoutApi.getErrorMessage(error);
        this.isLoading = false;
        this.changeDetector.markForCheck();
      },
    });
  }
}
