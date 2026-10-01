/** Serializable exercise fields returned by the workout API. */
export interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
  completed: boolean;
}

/** Current workout state and summary metrics. */
export interface WorkoutState {
  exercises: Exercise[];
  current: Exercise | null;
  total_exercises: number;
  progress: number;
  estimated_rest_seconds: number;
}

/** English API payload used to create an exercise. */
export interface ExerciseInput {
  name: string;
  sets: number;
  reps: number;
  weight_kg: number;
  rest_seconds: number;
}
