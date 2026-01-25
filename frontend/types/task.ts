/**
 * Task type definitions
 * Matches backend Pydantic schemas from Spec-1
 */

/**
 * Task object returned by backend
 * Matches backend TaskResponse schema
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: number;
  created_at: string;      // ISO 8601 format
  updated_at: string;      // ISO 8601 format
}

/**
 * Task creation request payload
 * POST /users/{user_id}/tasks
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * Task update request payload
 * PUT /users/{user_id}/tasks/{task_id}
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * Task completion toggle request
 * Used for checkbox toggle
 */
export interface TaskComplete {
  completed: boolean;
}
