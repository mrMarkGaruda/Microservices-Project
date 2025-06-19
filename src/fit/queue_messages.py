from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Schema for creating a workout message
class CreateWodMessage(BaseModel):
    email: str  # User's email address

# Schema for each exercise performed in a workout
class WorkoutPerformedExerciseSchema(BaseModel):
    exercise_id: int  # Unique identifier for the exercise

# Schema for the message sent when a workout is performed
class WorkoutPerformedMessage(BaseModel):
    user_email: str  # User's email address
    workout_id: int  # Unique identifier for the workout
    performed_at: datetime  # Timestamp of when the workout was performed
    exercises: List[WorkoutPerformedExerciseSchema] = Field(..., description="List of exercises performed in the workout")  # List of exercises in the workout
    event_type: str = "WorkoutPerformed"  # Type of the event
    event_version: str = "1.0"  # Version of the event schema