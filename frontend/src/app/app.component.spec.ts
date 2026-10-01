import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { WorkoutState } from './workout.model';

describe('AppComponent', () => {
  let httpTesting: HttpTestingController;

  const emptyState: WorkoutState = {
    exercises: [],
    current: null,
    total_exercises: 0,
    progress: 0,
    estimated_rest_seconds: 0,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('loads the workout and renders the empty state', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    httpTesting
      .expectOne('http://localhost:8000/api/workout')
      .flush(emptyState);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain(
      'Your workout starts here',
    );
    expect(fixture.nativeElement.textContent).toContain('Active workout');
  });

  it('renders exercises returned by the initial API request', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    httpTesting.expectOne('http://localhost:8000/api/workout').flush({
      exercises: [
        {
          id: 'squats',
          name: 'Squats',
          sets: 3,
          reps: 10,
          weight_kg: 20,
          rest_seconds: 60,
          completed: false,
        },
      ],
      current: {
        id: 'squats',
        name: 'Squats',
        sets: 3,
        reps: 10,
        weight_kg: 20,
        rest_seconds: 60,
        completed: false,
      },
      total_exercises: 1,
      progress: 0,
      estimated_rest_seconds: 120,
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Squats');
    expect(fixture.nativeElement.textContent).toContain('1 EXERCISES');
  });

  it('adds an exercise using the Python API', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    httpTesting
      .expectOne('http://localhost:8000/api/workout')
      .flush(emptyState);

    const component = fixture.componentInstance;
    component.exerciseForm.setValue({
      name: 'Squats',
      sets: 3,
      reps: 10,
      weightKg: 20,
      restSeconds: 60,
    });
    component.saveExercise();

    const request = httpTesting.expectOne('http://localhost:8000/api/workout');
    expect(request.request.method).toBe('POST');
    expect(request.request.body.name).toBe('Squats');
    request.flush({
      exercises: [
        {
          id: 'squats',
          name: 'Squats',
          sets: 3,
          reps: 10,
          weight_kg: 20,
          rest_seconds: 60,
          completed: false,
        },
      ],
      current: {
        id: 'squats',
        name: 'Squats',
        sets: 3,
        reps: 10,
        weight_kg: 20,
        rest_seconds: 60,
        completed: false,
      },
      total_exercises: 1,
      progress: 0,
      estimated_rest_seconds: 120,
    });

    expect(component.state.current?.name).toBe('Squats');
    expect(component.exerciseForm.controls.name.value).toBe('');
  });

  it('marks the workout complete after finishing the final exercise', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    httpTesting
      .expectOne('http://localhost:8000/api/workout')
      .flush(emptyState);

    const exercise = {
      id: 'bench-press',
      name: 'Bench press',
      sets: 3,
      reps: 10,
      weight_kg: 20,
      rest_seconds: 60,
      completed: false,
    };
    fixture.componentInstance.state = {
      exercises: [exercise],
      current: exercise,
      total_exercises: 1,
      progress: 0,
      estimated_rest_seconds: 120,
    };
    fixture.componentInstance.advance();

    httpTesting
      .expectOne('http://localhost:8000/api/workout/advance')
      .flush({
        exercises: [{ ...exercise, completed: true }],
        current: { ...exercise, completed: true },
        total_exercises: 1,
        progress: 100,
        estimated_rest_seconds: 120,
      });
    await fixture.whenStable();
    fixture.detectChanges();

    expect(fixture.componentInstance.isWorkoutComplete).toBeTrue();
    const nextButton: HTMLButtonElement =
      fixture.nativeElement.querySelector('.button-primary');
    expect(nextButton.disabled).toBeTrue();
    expect(nextButton.textContent).toContain('Workout complete');
  });
});
