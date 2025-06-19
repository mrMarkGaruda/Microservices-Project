# Import BaseModel and Field from pydantic for data validation
from pydantic import BaseModel, Field
# Import List and Optional for type hinting
from typing import List, Optional
# Import datetime for date/time fields
from datetime import datetime

# Define the schema for a single exercise performed in a workout
class WorkoutPerformedExerciseSchema(BaseModel):
    exercise_id: int  # ID of the exercise

# Define the schema for a workout performed message
class WorkoutPerformedMessage(BaseModel):
    user_email: str  # Email of the user
    workout_id: int  # ID of the workout
    performed_at: datetime  # Timestamp when the workout was performed
    exercises: List[WorkoutPerformedExerciseSchema] = Field(..., description="List of exercises performed in the workout")  # List of exercises
    event_type: str = "WorkoutPerformed"  # Type of event
    event_version: str = "1.0"  # Version of the event schema